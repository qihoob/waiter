# BaseSlotHandler.py
"""
基础槽位处理器，提供通用功能
"""

from typing import Dict, Any, Optional
from slot.SlotHandler import SlotHandler
from slot.ContextManager import get_context_manager
import logging

logger = logging.getLogger(__name__)

class BaseSlotHandler(SlotHandler):
    """基础槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        self.ctx_manager = get_context_manager()

    def _get_text_to_process(self, context: Dict[str, Any]) -> Optional[str]:
        """
        按优先级获取需要处理的文本

        Args:
            context: 处理上下文

        Returns:
            需要处理的文本，如果没有则返回None
        """
        # 按优先级获取文本
        text_sources = [
            context.get('cleaned_text'),
            context.get('input_text'),
            context.get('tokenized_text')
        ]

        for text in text_sources:
            if text:
                return text

        return None

    def _set_slot(self, context: Dict[str, Any], slot_name: str, slot_value: Any) -> bool:
        """
        统一设置槽位值

        Args:
            context: 处理上下文
            slot_name: 槽位名称
            slot_value: 槽位值

        Returns:
            bool: 是否设置成功
        """
        # 使用ContextManager设置槽位，包含验证
        success = self.ctx_manager.set_slot(slot_name, slot_value)
        if success:
            # 同步更新到context中
            if 'slots' not in context:
                context['slots'] = {}
            context['slots'][slot_name] = slot_value
        return success
