from typing import Dict, Any, Tuple, List
from slot.SlotHandler import SlotHandler
import re

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
        cleaned_text = context.get('cleaned_text', '')
        processed_text, extracted_info = self._preprocess_text(cleaned_text)
        tokenized_text = self._custom_tokenize(processed_text)
        enhanced_tokenized_text = self._enhance_tokenized_text(tokenized_text, cleaned_text)

        context.setdefault('slots', {}).update(extracted_info)
        context['tokenized_text'] = enhanced_tokenized_text
        return super().handle(context)

    # 在 TokenizationSlotHandler.py 中修复 _preprocess_text 方法
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


    def _custom_tokenize(self, text: str) -> str:
        """优化分词：支持多token中文数字组合（如“一 百 元”→“一百元”）"""
        from slot.global_vars import get_global_tokenizer
        tokenizer = get_global_tokenizer()
        tokens = tokenizer.tokenize(text)
        processed_tokens = []
        i = 0

        while i < len(tokens):
            # 处理中文数字组合（如“一 十”→“十”，“二 百”→“二百”）
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
                    processed_tokens.extend(num_tokens)
                    i += num_length
                    continue
            # 处理普通数量词
            elif self._is_quantity_token(tokens, i):
                quantity_token = self._merge_quantity_components(tokens, i)
                processed_tokens.append(quantity_token)
                i += self._get_quantity_component_count(tokens, i)
            else:
                processed_tokens.append(tokens[i])
                i += 1

        return ' '.join(processed_tokens)

    def _enhance_tokenized_text(self, tokenized_text: str, original_text: str) -> str:
        """增强分词结果：将数量词还原到原文位置，而非追加"""
        # 步骤1：将原始分词和数量词位置结合，构建带位置的token列表
        token_list = tokenized_text.split()
        if not self.quantity_positions:
            return tokenized_text

        # 步骤2：将原文按数量词分割为片段，插入标准化数量词
        segments = []
        last_end = 0
        for pos in self.quantity_positions:
            # 取数量词前的文本片段
            prefix = original_text[last_end:pos["start"]].strip()
            if prefix:
                # 分词并保留前缀
                prefix_tokens = self._tokenize_segment(prefix)
                segments.extend(prefix_tokens)
            # 插入标准化数量词（如[人数:3]）
            segments.append(f"[{pos['slot']}:{pos['value']}]")
            last_end = pos["end"]

        # 处理剩余文本
        suffix = original_text[last_end:].strip()
        if suffix:
            suffix_tokens = self._tokenize_segment(suffix)
            segments.extend(suffix_tokens)

        # 步骤3：合并结果，去重空token
        return ' '.join([t for t in segments if t])

    def _tokenize_segment(self, text: str) -> List[str]:
        """辅助方法：对文本片段进行分词"""
        from slot.global_vars import get_global_tokenizer
        tokenizer = get_global_tokenizer()
        return tokenizer.tokenize(text)

    def _is_cn_number_series(self, tokens: List[str], index: int) -> bool:
        """判断是否为连续的中文数字token（如“一 十”“二 百 三”）"""
        if index >= len(tokens):
            return False
        return tokens[index] in self.cn_basic_map and not self._is_unit_token(tokens[index])

    def _merge_cn_number_series(self, tokens: List[str], index: int) -> Tuple[List[str], int]:
        """合并连续的中文数字token（如“一 百 二”→["一百二"], 3）"""
        merged = []
        length = 0
        i = index
        while i < len(tokens) and self._is_cn_number_series(tokens, i):
            merged.append(tokens[i])
            length += 1
            i += 1
        return merged, length

    def _is_quantity_token(self, tokens: List[str], index: int) -> bool:
        """判断是否为数量词组合（含中文数字组合）"""
        if index >= len(tokens):
            return False
        # 单token数量词（如“3人”“半份”）
        if self._contains_number_and_unit(tokens[index]):
            return True
        # 多token数量词（如“10 元”“两 份儿”）
        if index + 1 < len(tokens):
            return (self._is_number_token(tokens[index]) and
                    self._is_unit_token(tokens[index + 1]))
        return False

    def _merge_quantity_components(self, tokens: List[str], index: int) -> str:
        """合并数量词组件（数字+单位）"""
        if self._contains_number_and_unit(tokens[index]):
            return tokens[index]
        return tokens[index] + tokens[index + 1]

    def _get_quantity_component_count(self, tokens: List[str], index: int) -> int:
        """获取数量词组合的token数量"""
        if self._contains_number_and_unit(tokens[index]):
            return 1
        return 2

    def _is_number_token(self, token: str) -> bool:
        """判断是否为数字token（支持中文数字组合和小数）"""
        if re.match(r'^\d+(\.\d+)?$', token):
            return True
        # 中文数字组合（如“二十”“一百二”）
        for char in token:
            if char not in self.cn_basic_map:
                return False
        return len(token) > 0

    def _is_unit_token(self, token: str) -> bool:
        return token in self.unit_set

    def _contains_number_and_unit(self, token: str) -> bool:
        """判断单token是否包含数字和单位（支持复杂组合）"""
        if not token:
            return False
        # 分离数字和单位部分（如“一百元”→数字“一百”，单位“元”）
        unit_part = None
        for unit in self.unit_set:
            if token.endswith(unit):
                unit_part = unit
                num_part = token[:-len(unit)]
                break
        if not unit_part:
            return False
        # 检查数字部分是否有效
        return self._is_number_token(num_part)

    def _cn_num_to_arabic(self, cn_num: str) -> float or None:
        """将中文数字（支持组合）转换为阿拉伯数字"""
        # 处理阿拉伯数字
        if re.match(r'^\d+(\.\d+)?$', cn_num):
            return float(cn_num) if '.' in cn_num else int(cn_num)

        # 处理中文数字组合（如“二十”“一百二”“两半”）
        total = 0
        current = 0
        for char in cn_num:
            if char not in self.cn_basic_map:
                return None  # 包含无效字符
            val = self.cn_basic_map[char]
            if val in (10, 100, 1000):  # 十/百/千
                if current == 0:
                    current = 1  # 处理“十”→10，“百”→100
                total += current * val
                current = 0
            elif char == "半":  # 处理“半”（如“三个半”→3.5）
                total += current + 0.5
                current = 0
            else:  # 一/二/.../九/两
                current += val
        total += current  # 加上剩余的个位数
        return total if total != 0 else None  # 避免返回0（无效数字）

def test_handle_method():
    """测试 TokenizationSlotHandler 的 handle 方法"""
    print("=" * 60)
    print("测试 TokenizationSlotHandler 的 handle 方法")
    print("=" * 60)

    handler = TokenizationSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "基本分词测试",
            "context": {
                "cleaned_text": "我想吃麻婆豆腐和宫保鸡丁"
            }
        },
        {
            "name": "数字与单位组合处理",
            "context": {
                "cleaned_text": "请给我来4份牛肉面和2杯咖啡"
            }
        },
        {
            "name": "预处理功能-人数",
            "context": {
                "cleaned_text": "我们一共3个人聚餐，需要5份菜"
            }
        },
        {
            "name": "预处理功能-预算",
            "context": {
                "cleaned_text": "预算300元以内，大概4个人吃"
            }
        },
        {
            "name": "预处理功能-份数",
            "context": {
                "cleaned_text": "我要半份牛排和两盘汤"
            }
        },
        {
            "name": "复杂句子",
            "context": {
                "cleaned_text": "5位客人用餐，预算一百元左右，需要火锅和烧烤"
            }
        },
        {
            "name": "不包含数字的文本",
            "context": {
                "cleaned_text": "今天天气很好，想吃点清淡的"
            }
        },
        {
            "name": "已有slots的上下文",
            "context": {
                "cleaned_text": "3个人吃200元的菜",
                "slots": {
                    "已存在": "值"
                }
            }
        },
        {
            "name": "中文数字组合测试",
            "context": {
                "cleaned_text": "我们要二十个人的套餐，预算一百五十元"
            }
        },
        {
            "name": "多个数量词冲突处理",
            "context": {
                "cleaned_text": "2人3份菜，后来又加了3人2份菜"
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"输入文本: {test_case['context'].get('cleaned_text', '')}")

        try:
            # 保存原始上下文用于比较
            original_context = test_case['context'].copy()

            # 执行处理
            result_context = handler.handle(test_case['context'].copy())

            # 输出结果
            print(f"  分词结果: {result_context.get('tokenized_text', '')}")
            print(f"  提取的槽位: {result_context.get('slots', {})}")

            # 验证关键字段是否存在
            assert 'tokenized_text' in result_context, "结果中缺少 tokenized_text 字段"
            assert 'slots' in result_context, "结果中缺少 slots 字段"

            # 验证 slots 是字典类型
            assert isinstance(result_context['slots'], dict), "slots 应该是字典类型"

            # 如果原始上下文中有 slots，验证合并是否正确
            if 'slots' in original_context:
                for key, value in original_context['slots'].items():
                    assert key in result_context['slots'], f"原始slots中的 {key} 丢失"
                    # 注意：如果有冲突，新提取的值会覆盖原始值

            print("  ✓ 测试通过")

        except Exception as e:
            print(f"  ✗ 处理出错: {e}")
            import traceback
            traceback.print_exc()

def test_edge_cases():
    """测试边缘情况"""
    print("\n" + "=" * 60)
    print("测试边缘情况")
    print("=" * 60)

    handler = TokenizationSlotHandler()

    edge_cases = [
        {
            "name": "空文本",
            "context": {
                "cleaned_text": ""
            }
        },
        {
            "name": "只有空格",
            "context": {
                "cleaned_text": "   "
            }
        },
        {
            "name": "只有数字",
            "context": {
                "cleaned_text": "123"
            }
        },
        {
            "name": "无意义文本",
            "context": {
                "cleaned_text": "asdfghjkl"
            }
        },
        {
            "name": "边界数字表达",
            "context": {
                "cleaned_text": "一千人吃一百份菜花了一万元"
            }
        }
    ]

    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n边缘测试 {i}: {test_case['name']}")
        print(f"输入文本: '{test_case['context'].get('cleaned_text', '')}'")

        try:
            result_context = handler.handle(test_case['context'].copy())
            print(f"  分词结果: '{result_context.get('tokenized_text', '')}'")
            print(f"  提取的槽位: {result_context.get('slots', {})}")
            print("  ✓ 处理完成（无异常）")
        except Exception as e:
            print(f"  ✗ 出错: {e}")

def test_quantity_position_tracking():
    """测试数量词位置跟踪功能"""
    print("\n" + "=" * 60)
    print("测试数量词位置跟踪功能")
    print("=" * 60)

    handler = TokenizationSlotHandler()

    test_cases = [
        "我要3份牛肉面和2杯咖啡",
        "5位客人用餐预算一百元",
        "三个人吃五份菜"
    ]

    for i, text in enumerate(test_cases, 1):
        print(f"\n位置跟踪测试 {i}: {text}")

        try:
            context = {"cleaned_text": text}
            result_context = handler.handle(context)

            print(f"  原始数量词位置: {handler.quantity_positions}")
            print(f"  增强分词结果: {result_context.get('tokenized_text')}")
            print(f"  提取槽位: {result_context.get('slots')}")

            # 验证位置信息是否正确记录
            if handler.quantity_positions:
                for pos in handler.quantity_positions:
                    assert "start" in pos, "位置信息缺少 start 字段"
                    assert "end" in pos, "位置信息缺少 end 字段"
                    assert "text" in pos, "位置信息缺少 text 字段"
                    assert "slot" in pos, "位置信息缺少 slot 字段"
                    assert "value" in pos, "位置信息缺少 value 字段"
                print("  ✓ 位置信息完整")
            else:
                print("  - 无数量词位置信息")

        except Exception as e:
            print(f"  ✗ 出错: {e}")

def test_chinese_number_conversion():
    """测试中文数字转换功能"""
    print("\n" + "=" * 60)
    print("测试中文数字转换功能")
    print("=" * 60)

    handler = TokenizationSlotHandler()

    # 直接测试中文数字转换方法
    cn_number_tests = [
        ("一", 1),
        ("二", 2),
        ("十", 10),
        ("二十", 20),
        ("二十五", 25),
        ("一百", 100),
        ("一百二", 120),
        ("一百二十三", 123),
        ("一千", 1000),
        ("一千零一", 1001),
        ("两千", 2000),
        (" half", 0.5),  # 半
        ("两", 2),
        ("三半", 3.5)
    ]

    print("直接测试中文数字转换:")
    for cn_num, expected in cn_number_tests:
        try:
            result = handler._cn_num_to_arabic(cn_num)
            status = "✓" if result == expected else "✗"
            print(f"  '{cn_num}' -> {result} (期望: {expected}) {status}")
        except Exception as e:
            print(f"  '{cn_num}' -> 错误: {e} ✗")

    # 通过 handle 方法测试
    print("\n通过 handle 方法测试:")
    conversion_test_cases = [
        {
            "name": "简单中文数字",
            "context": {
                "cleaned_text": "我要三份米饭"
            }
        },
        {
            "name": "复合中文数字",
            "context": {
                "cleaned_text": "我们需要二十五个人的座位"
            }
        },
        {
            "name": "带半的数字",
            "context": {
                "cleaned_text": "给我来三个半苹果"
            }
        }
    ]

    for test_case in conversion_test_cases:
        print(f"\n{test_case['name']}: {test_case['context']['cleaned_text']}")
        try:
            result = handler.handle(test_case['context'].copy())
            print(f"  分词结果: {result.get('tokenized_text')}")
            print(f"  提取槽位: {result.get('slots')}")
        except Exception as e:
            print(f"  出错: {e}")

if __name__ == "__main__":
    print("开始测试 TokenizationSlotHandler 的 handle 方法")

    # 运行各项测试
    test_handle_method()
    test_edge_cases()
    test_quantity_position_tracking()
    test_chinese_number_conversion()

    print("\n" + "=" * 60)
    print("所有测试完成!")