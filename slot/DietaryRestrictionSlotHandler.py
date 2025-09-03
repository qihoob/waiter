# DietaryRestrictionSlotHandler.py (优化版)
"""
忌口槽位处理器
"""

from typing import Dict, Any, Optional
from slot.BaseSlotHandler import BaseSlotHandler
from prompt_builder.config import SLOT_DICT
import logging

logger = logging.getLogger(__name__)

class DietaryRestrictionSlotHandler(BaseSlotHandler):
    """忌口槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取忌口词典
        self.dietary_restriction_keywords = SLOT_DICT.get("忌口", [])
        # 按长度排序，优先匹配长词汇
        self.dietary_restriction_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)

            if text_to_process:
                # 提取忌口信息
                dietary_restriction_info = self._extract_dietary_restriction_info(text_to_process)

                # 如果提取到忌口信息，则更新slots
                if dietary_restriction_info:
                    # 忌口可能有多个，以列表形式存储
                    slots = context.setdefault('slots', {})
                    if '忌口' not in slots:
                        slots['忌口'] = []

                    if isinstance(slots['忌口'], list):
                        slots['忌口'].append(dietary_restriction_info)
                    else:
                        slots['忌口'] = [slots['忌口'], dietary_restriction_info]

                    self._set_slot(context, '忌口', slots['忌口'])
                    logger.info(f"识别到忌口: {dietary_restriction_info}")

        except Exception as e:
            logger.error(f"忌口槽位处理出错: {e}")

        return super().handle(context)

    def _extract_dietary_restriction_info(self, text: str) -> Optional[str]:
        """
        从文本中提取忌口信息

        Args:
            text: 输入文本

        Returns:
            识别到的忌口信息，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的忌口信息
        for restriction in self.dietary_restriction_keywords:
            # 将忌口词也转为小写进行匹配
            restriction_lower = restriction.lower()

            # 精确匹配整个词
            if restriction_lower in processed_text:
                return restriction  # 返回原始大小写的忌口词

        return None
