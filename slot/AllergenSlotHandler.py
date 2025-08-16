# AllergenSlotHandler.py (优化版)
"""
过敏原槽位处理器
"""

from typing import Dict, Any, Optional
from slot.BaseSlotHandler import BaseSlotHandler
from prompt_builder.config import SLOT_DICT
import logging

logger = logging.getLogger(__name__)

class AllergenSlotHandler(BaseSlotHandler):
    """过敏原槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取过敏原词典
        self.allergen_keywords = SLOT_DICT.get("过敏原", [])
        # 按长度排序，优先匹配长词汇
        self.allergen_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)

            if text_to_process:
                # 提取过敏原信息
                allergen_info = self._extract_allergen_info(text_to_process)

                # 如果提取到过敏原信息，则更新slots
                if allergen_info:
                    # 过敏原可能有多个，以列表形式存储
                    slots = context.setdefault('slots', {})
                    if '过敏原' not in slots:
                        slots['过敏原'] = []

                    if isinstance(slots['过敏原'], list):
                        slots['过敏原'].append(allergen_info)
                    else:
                        slots['过敏原'] = [slots['过敏原'], allergen_info]

                    self._set_slot(context, '过敏原', slots['过敏原'])
                    logger.info(f"识别到过敏原: {allergen_info}")

        except Exception as e:
            logger.error(f"过敏原槽位处理出错: {e}")

        return super().handle(context)

    def _extract_allergen_info(self, text: str) -> Optional[str]:
        """
        从文本中提取过敏原信息

        Args:
            text: 输入文本

        Returns:
            识别到的过敏原信息，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的过敏原信息
        for allergen in self.allergen_keywords:
            # 将过敏原词也转为小写进行匹配
            allergen_lower = allergen.lower()

            # 精确匹配整个词
            if allergen_lower in processed_text:
                return allergen  # 返回原始大小写的过敏原词

        return None
