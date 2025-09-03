# TokenizationSlotHandler.py (优化版)
from typing import Dict, Any, Tuple, List
from slot.SlotHandler import SlotHandler
import re
from slot.ContextManager import get_context_manager

class TokenizationSlotHandler(SlotHandler):
    """增强版分词处理器，优化数量词处理和信息合并逻辑"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 数量词模式（支持中文数字组合和更灵活的表达）
        self.patterns = {
            "人数": re.compile(r"((?:\d+|一|二|三|四|五|六|七|八|九|十|百|千|两)(?:十|百|千)?)\s*(人|位|个|名)"),
            "预算": re.compile(r"((?:\d+(\.\d+)?|一|二|三|四|五|六|七|八|九|十|百|千|两)(?:十|百|千)?)\s*(元|块|以内|以下|左右|块钱)"),
            "份数": re.compile(r"((?:\d+(\.\d+)?|一|二|三|四|五|六|七|八|九|十|半|两)(?:十|百|千)?)\s*(份|份儿|盘|碗|个|道)")
        }
        # 中文数字基础映射
        self.cn_basic_map = {
            "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
            "百": 100, "千": 1000, "两": 2, "半": 0.5
        }
        # 扩展单位列表
        self.unit_set = {'人', '位', '个', '名', '元', '块', '份', '份儿',
                         '盘', '碗', '道', '杯', '瓶', '桌', '斤', '两', '克'}
        # 记录数量词在原文中的位置（用于还原）
        self.quantity_positions: List[Dict] = []

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.quantity_positions = []  # 重置位置记录

        # 使用ContextManager确保数据一致性
        ctx_manager = get_context_manager()
        ctx_manager.update_context({'input': context})

        try:
            cleaned_text = context.get('cleaned_text', '')
            processed_text, extracted_info = self._preprocess_text(cleaned_text)
            tokenized_text = self._custom_tokenize(processed_text)
            enhanced_tokenized_text = self._enhance_tokenized_text(tokenized_text, cleaned_text)

            # 更新slots信息
            for key, value in extracted_info.items():
                ctx_manager.set_slot(key, value)

            # 更新context
            context_updates = {
                'input': {
                    'tokenized_text': enhanced_tokenized_text
                },
                'recognition': {
                    'slots': ctx_manager.context['recognition']['slots']
                }
            }
            ctx_manager.update_context(context_updates)

            # 同步回原始context
            context.update(ctx_manager.get_context()['input'])
            context.update(ctx_manager.get_context()['recognition'])

        except Exception as e:
            ctx_manager.add_error(self.__class__.__name__, e)
            logger.error(f"Tokenization处理出错: {e}")

        return super().handle(context)

    def _preprocess_text(self, text: str) -> Tuple[str, Dict[str, float]]:
        """增强预处理：支持中文数字组合，记录数量词位置"""
        extracted_info = {}
        processed_text = text
        original_text = text  # 保留原文用于位置计算

        for key, pattern in self.patterns.items():
            matches = list(pattern.finditer(original_text))  # 获取匹配对象（含位置）
            if matches:
                # 取最后一个有效匹配
                last_match = matches[-1]
                num_str = last_match.group(1)
                # 修复：正确获取单位部分
                if len(last_match.groups()) >= 2:
                    unit_str = last_match.group(2)  # 单位部分
                else:
                    unit_str = last_match.group(len(last_match.groups()))  # 最后一个分组

                # 转换数字（支持组合如"二十""一百二"）
                num_value = self._cn_num_to_arabic(num_str)
                if num_value is not None:
                    extracted_info[key] = num_value
                    # 记录数量词位置和原始文本（用于后续还原）
                    self.quantity_positions.append({
                        "start": last_match.start(),
                        "end": last_match.end(),
                        "text": last_match.group(),
                        "slot": key,
                        "value": num_value
                    })
                # 移除所有匹配项（避免重复处理）
                processed_text = pattern.sub("", processed_text)

        # 按位置排序（确保还原时顺序正确）
        self.quantity_positions.sort(key=lambda x: x["start"])
        return processed_text.strip(), extracted_info

    def _cn_num_to_arabic(self, cn_num: str) -> float or None:
        """将中文数字（支持组合）转换为阿拉伯数字"""
        # 处理阿拉伯数字
        if re.match(r'^\d+(\.\d+)?$', cn_num):
            return float(cn_num) if '.' in cn_num else int(cn_num)

        # 处理中文数字组合（如"二十""一百二""两半"）
        total = 0
        current = 0
        for char in cn_num:
            if char not in self.cn_basic_map:
                return None  # 包含无效字符
            val = self.cn_basic_map[char]
            if val in (10, 100, 1000):  # 十/百/千
                if current == 0:
                    current = 1  # 处理"十"→10，"百"→100
                total += current * val
                current = 0
            elif char == "半":  # 处理"半"（如"三个半"→3.5）
                total += current + 0.5
                current = 0
            else:  # 一/二/.../九/两
                current += val
        total += current  # 加上剩余的个位数
        return total if total != 0 else None  # 避免返回0（无效数字）

    def _custom_tokenize(self, text: str) -> str:
        """优化分词：支持多token中文数字组合（如"一 百 元"→"一百元"）"""
        from slot.global_vars import get_global_tokenizer
        tokenizer = get_global_tokenizer()
        tokens = tokenizer.tokenize(text)
        processed_tokens = []
        i = 0

        while i < len(tokens):
            # 处理中文数字组合（如"一 十"→"十"，"二 百"→"二百"）
            if self._is_cn_number_series(tokens, i):
                # 合并连续的中文数字token
                num_tokens, num_length = self._merge_cn_number_series(tokens, i)
                # 检查后续是否有单位
                if i + num_length < len(tokens) and self._is_unit_token(tokens[i + num_length]):
                    unit_token = tokens[i + num_length]
                    merged_token = ''.join(num_tokens) + unit_token
                    processed_tokens.append(merged_token)
                    i += num_length + 1  # 跳过数字+单位
                    continue
                else:
                    # 无单位时直接合并数字
                    processed_tokens.append(''.join(num_tokens))
                    i += num_length
                    continue

            token = tokens[i]

            # 检查是否是数字+单位的组合（如"4人"）
            if i < len(tokens) - 1:
                # 检查当前token是否为数字，下一个token是否为单位词
                if self._is_number_token(token) and self._is_unit_token(tokens[i+1]):
                    # 合并数字和单位为一个token
                    combined_token = token + tokens[i+1]
                    processed_tokens.append(combined_token)
                    i += 2  # 跳过下一个token
                    continue

            # 检查单个token中是否包含数字和单位（如"4人"作为一个token）
            if self._contains_number_and_unit(token):
                processed_tokens.append(token)
                i += 1
                continue

            # 其他情况直接添加token
            processed_tokens.append(token)
            i += 1

        return ' '.join(processed_tokens)

    def _is_number_token(self, token: str) -> bool:
        """判断token是否为数字"""
        return bool(re.match(r'^\d+(\.\d+)?$', token))

    def _is_unit_token(self, token: str) -> bool:
        """判断token是否为单位词"""
        return token in self.unit_set

    def _contains_number_and_unit(self, token: str) -> bool:
        """判断token是否包含数字和单位（如"4人"）"""
        # 检查是否包含数字和单位字符
        has_number = bool(re.search(r'\d', token))
        has_unit = any(unit in token for unit in self.unit_set)
        return has_number and has_unit

    def _is_cn_number_series(self, tokens: List[str], start_index: int) -> bool:
        """判断是否为连续的中文数字序列"""
        i = start_index
        while i < len(tokens) and tokens[i] in self.cn_basic_map:
            # 检查是否是有效的数字序列（避免误判）
            if tokens[i] in ['十', '百', '千'] and (i == start_index or tokens[i-1] in ['十', '百', '千']):
                # 避免连续的单位词（如"十百"）
                break
            i += 1
        return i > start_index  # 至少有一个中文数字

    def _merge_cn_number_series(self, tokens: List[str], start_index: int) -> Tuple[List[str], int]:
        """合并连续的中文数字token"""
        i = start_index
        number_tokens = []
        while i < len(tokens) and tokens[i] in self.cn_basic_map:
            # 检查是否是有效的数字序列
            if tokens[i] in ['十', '百', '千'] and (i == start_index or tokens[i-1] in ['十', '百', '千']):
                break
            number_tokens.append(tokens[i])
            i += 1
        return number_tokens, i - start_index

    def _enhance_tokenized_text(self, tokenized_text: str, original_text: str) -> str:
        """增强分词文本，将数量词位置信息还原到分词结果中"""
        if not self.quantity_positions:
            return tokenized_text

        # 将原始文本中的数量词位置信息添加到分词结果中
        enhanced_text = tokenized_text
        offset = 0  # 用于跟踪插入文本后的偏移量

        for pos_info in self.quantity_positions:
            # 在分词文本中适当位置插入数量词信息
            # 这里可以添加更复杂的逻辑来精确定位插入点
            slot_tag = f"[{pos_info['slot']}:{pos_info['value']}]"
            # 简单实现：在文本末尾添加槽位标记
            enhanced_text += f" {slot_tag}"

        return enhanced_text.strip()
