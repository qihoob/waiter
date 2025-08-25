# HealthPreferenceSlotHandler.py (优化版)
"""
健康偏好槽位处理器
从输入文本中抽取健康/营养相关偏好关键词，并写入 context['slots']['健康偏好']。
"""

from typing import Dict, Any, Optional, List
from slot.BaseSlotHandler import BaseSlotHandler
from prompt_builder.config import SLOT_DICT
import logging

logger = logging.getLogger(__name__)


class HealthPreferenceSlotHandler(BaseSlotHandler):
    """健康偏好槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取健康偏好词典
        # 关键词示例：低脂、少油少盐、无糖、高蛋白、清淡、轻食、低钠等 [1]
        self.health_keywords: List[str] = SLOT_DICT.get("健康偏好", [])
        # 按长度排序，优先匹配更长的词，避免被短词提前命中 [2]
        self.health_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取需要处理的文本（父类里通常会从 context 中组合用户话术等）[2]
            text_to_process = self._get_text_to_process(context)

            if text_to_process:
                # 提取健康偏好信息（可能有多个）
                prefs = self._extract_health_prefs(text_to_process)

                # 如果提取到，则更新 slots
                if prefs:
                    # 如果已有槽位，做并集合并，避免覆盖
                    existing = self._get_slot(context, '健康偏好')
                    if isinstance(existing, list):
                        merged = list(dict.fromkeys(existing + prefs))  # 去重并保持顺序
                    elif isinstance(existing, str) and existing:
                        merged = list(dict.fromkeys([existing] + prefs))
                    else:
                        merged = prefs

                    self._set_slot(context, '健康偏好', merged)
                    logger.info(f"识别到健康偏好: {merged}")

        except Exception as e:
            logger.error(f"健康偏好槽位处理出错: {e}")

        # 继续责任链
        return super().handle(context)

    def _extract_health_prefs(self, text: str) -> Optional[List[str]]:
        """
        从文本中提取健康偏好关键词（可能多选）

        Args:
            text: 输入文本

        Returns:
            匹配到的健康偏好关键词列表；若无则返回 None
        """
        if not text:
            return None

        processed_text = text.lower().strip()
        found: List[str] = []

        # 长词优先匹配，避免短词误伤
        for kw in self.health_keywords:
            kw_lower = kw.lower()
            if kw_lower in processed_text:
                found.append(kw)  # 返回原始大小写的关键词

        # 去重后返回
        if found:
            # 使用 dict.fromkeys 保序去重
            return list(dict.fromkeys(found))

        return None