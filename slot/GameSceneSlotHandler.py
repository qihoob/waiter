# GameSlotHandler.py (优化版)
"""
游戏槽位处理器
"""

from typing import Dict, Any, Optional
from slot.BaseSlotHandler import BaseSlotHandler
from prompt_builder.config import SLOT_DICT
import logging

logger = logging.getLogger(__name__)

class GameSlotHandler(BaseSlotHandler):
    """游戏槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取游戏词典
        self.game_keywords = SLOT_DICT.get("游戏", [])
        # 按长度排序，优先匹配长词汇
        self.game_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)

            if text_to_process:
                # 提取游戏信息
                game_info = self._extract_game_info(text_to_process)

                # 如果提取到游戏信息，则更新slots
                if game_info:
                    self._set_slot(context, '游戏', game_info)
                    logger.info(f"识别到游戏: {game_info}")

        except Exception as e:
            logger.error(f"游戏槽位处理出错: {e}")

        return super().handle(context)

    def _extract_game_info(self, text: str) -> Optional[str]:
        """
        从文本中提取游戏信息

        Args:
            text: 输入文本

        Returns:
            识别到的游戏名称，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的游戏
        for game in self.game_keywords:
            # 将游戏名称也转为小写进行匹配
            game_lower = game.lower()

            # 精确匹配整个词
            if game_lower in processed_text:
                return game  # 返回原始大小写的游戏名称

        return None
