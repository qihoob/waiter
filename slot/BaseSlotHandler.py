# BaseSlotHandler.py
from typing import Dict, Any, Optional
from slot.SlotHandler import SlotHandler
from slot.ContextManager import get_context_manager

class BaseSlotHandler(SlotHandler):
    """槽位处理器基类"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        self.ctx_manager = get_context_manager()

    def _get_text_to_process(self, context: Dict[str, Any]) -> Optional[str]:
        """按优先级获取处理文本"""
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
        """统一设置槽位"""
        success = self.ctx_manager.set_slot(slot_name, slot_value)
        if success and 'slots' in context:
            context['slots'][slot_name] = slot_value
        return success
