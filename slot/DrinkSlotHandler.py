# DrinkSlotHandler.py (优化版)
"""
饮品槽位处理器
"""

from typing import Dict, Any, Optional
from slot.BaseSlotHandler import BaseSlotHandler
from prompt_builder.config import SLOT_DICT
import logging

logger = logging.getLogger(__name__)

class DrinkSlotHandler(BaseSlotHandler):
    """饮品槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取饮品词典
        self.drink_keywords = SLOT_DICT.get("饮品", [])
        # 按长度排序，优先匹配长词汇
        self.drink_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)

            if text_to_process:
                # 提取饮品信息
                drink_info = self._extract_drink_info(text_to_process)

                # 如果提取到饮品信息，则更新slots
                if drink_info:
                    self._set_slot(context, '饮品', drink_info)
                    logger.info(f"识别到饮品: {drink_info}")

        except Exception as e:
            logger.error(f"饮品槽位处理出错: {e}")

        return super().handle(context)

    def _extract_drink_info(self, text: str) -> Optional[str]:
        """
        从文本中提取饮品信息

        Args:
            text: 输入文本

        Returns:
            识别到的饮品名称，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的饮品
        for drink in self.drink_keywords:
            # 将饮品名称也转为小写进行匹配
            drink_lower = drink.lower()

            # 精确匹配整个词
            if drink_lower in processed_text:
                return drink  # 返回原始大小写的饮品名称

        return None
