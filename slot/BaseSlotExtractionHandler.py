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

    def _extract_numeric_slots(self, text):
        """统一提取数字型槽位"""
        numeric_slots = {}

        # 提取人数 - 扩展支持多种表达方式
        MIN_PERSONS = 1
        MAX_PERSONS = 20

        if m := re.search(r'(\d+)个?[人位份餐杯瓶盘碗]', text):
            count = int(m.group(1))
            if MIN_PERSONS <= count <= MAX_PERSONS:
                numeric_slots["人数"] = count

        # 提取预算
        if m := re.search(r'(\d{2,4})元', text):
            numeric_slots["预算"] = int(m.group(1))

        return numeric_slots
