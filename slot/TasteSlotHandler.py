# TasteSlotHandler.py (优化版)
"""
口味槽位处理器
"""

from typing import Dict, Any, Optional
from slot.BaseSlotHandler import BaseSlotHandler
from prompt_builder.config import SLOT_DICT
import logging

logger = logging.getLogger(__name__)

class TasteSlotHandler(BaseSlotHandler):
    """口味槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取口味词典
        self.taste_keywords = SLOT_DICT.get("口味", [])
        # 按长度排序，优先匹配长词汇
        self.taste_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)

            if text_to_process:
                # 提取口味信息
                taste_info = self._extract_taste_info(text_to_process)

                # 如果提取到口味信息，则更新slots
                if taste_info:
                    self._set_slot(context, '口味', taste_info)
                    logger.info(f"识别到口味: {taste_info}")

        except Exception as e:
            logger.error(f"口味槽位处理出错: {e}")

        return super().handle(context)

    def _extract_taste_info(self, text: str) -> Optional[str]:
        """
        从文本中提取口味信息

        Args:
            text: 输入文本

        Returns:
            识别到的口味，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的口味
        for taste in self.taste_keywords:
            # 将口味词也转为小写进行匹配
            taste_lower = taste.lower()

            # 精确匹配整个词
            if taste_lower in processed_text:
                return taste  # 返回原始大小写的口味词

        return None
