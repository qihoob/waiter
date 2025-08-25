# SceneSlotHandler.py (优化版)
from typing import Dict, Any, Optional
from slot.BaseSlotHandler import BaseSlotHandler
from prompt_builder.config import SLOT_DICT
import logging

logger = logging.getLogger(__name__)

class SceneSlotHandler(BaseSlotHandler):
    """场景槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取场景词典
        self.scene_keywords = SLOT_DICT.get("场景", [])
        # 按长度排序，优先匹配长词汇
        self.scene_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)

            if text_to_process:
                # 提取场景信息
                scene_info = self._extract_scene_info(text_to_process)

                # 如果提取到场景信息，则更新slots
                if scene_info:
                    self._set_slot(context, '场景', scene_info)
                    logger.info(f"识别到场景: {scene_info}")

        except Exception as e:
            logger.error(f"场景槽位处理出错: {e}")

        return super().handle(context)

    def _extract_scene_info(self, text: str) -> Optional[str]:
        """
        从文本中提取场景信息

        Args:
            text: 输入文本

        Returns:
            识别到的场景，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的场景
        for scene in self.scene_keywords:
            # 将场景词也转为小写进行匹配
            scene_lower = scene.lower()

            # 精确匹配整个词
            if scene_lower in processed_text:
                return scene  # 返回原始大小写的场景词

        return None
