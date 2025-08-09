# E:\work\waiter\slot\BaseSlotExtractionHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
from fuzzywuzzy import process
import re
from prompt_builder.config import SLOT_DICT
import logging

logger = logging.getLogger(__name__)

class BaseSlotExtractionHandler(SlotHandler):
    """基础槽位提取处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 提取槽位信息
            context['slots'] = self._extract_slots(
                context['tokenized_text'], is_tokenized=True
            )
            logger.info(f"提取到槽位: {context['slots']}")
        except Exception as e:
            logger.warning(f"槽位提取失败: {e}")
            context['slots'] = {}

        return super().handle(context)

    def _extract_slots(self, text: str, threshold=80, tokenizer=None, is_tokenized=False) -> dict:
        """
        从文本中提取槽位信息

        Args:
            text: 输入文本
            threshold: 模糊匹配阈值
            tokenizer: 可选的外部分词器
            is_tokenized: 表示输入是否已分词

        Returns:
            dict: 提取到的槽位字典
        """
        slots = {}

        # 获取分词器并进行分词处理
        if not is_tokenized:
            from global_vars import get_global_tokenizer
            tokenizer = tokenizer or get_global_tokenizer()
            tokenized_text = tokenizer.tokenize(text)
        else:
            tokenized_text = text

        # 1. 数字型槽位提取
        slots.update(self._extract_numeric_slots(tokenized_text))

        # 2. 精确关键词匹配
        for slot_name, keywords in SLOT_DICT.items():
            try:
                # 精确匹配（基于分词后的结果）
                matched = next((keyword for keyword in keywords if keyword in tokenized_text), None)

                # 若未匹配，尝试模糊匹配
                if not matched:
                    matched, score = process.extractOne(tokenized_text, keywords)
                    if score < threshold:
                        continue

                # 设置槽位值
                if slot_name in ["忌口", "过敏原"]:
                    slots.setdefault(slot_name, []).append(matched)
                else:
                    slots[slot_name] = matched

            except Exception as e:
                logger.warning(f"提取槽位 {slot_name} 时出错: {e}")
                continue

        return slots

    def extract_people_count(text):
        # 中文数字到阿拉伯数字的映射
        chinese_to_num = {
            '一': 1,
            '二': 2,
            '两': 2,
            '三': 3,
            '四': 4,
            '五': 5,
            '六': 6,
            '七': 7,
            '八': 8,
            '九': 9,
            '十': 10
        }

        # 表示人的关键词
        people_keywords = ['人', '位', '客']

        # 再尝试匹配中文数字 + 关键词的情况
        for keyword in people_keywords:
            for chinese_num, num in chinese_to_num.items():
                if chinese_num + keyword in text:
                    return num

        # 特殊情况："一个人吃饭" 这种结构
        pattern = r'([一二两三四五六七八九十]|[\d]+)个(人)'
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1)
            if num_str.isdigit():
                return int(num_str)
            return chinese_to_num.get(num_str, None)

        # 提取预算
        budget_match = re.search(r'(\d{2,4})元', text)
        if budget_match:
            numeric_slots["预算"] = int(budget_match.group(1))

        return numeric_slots
