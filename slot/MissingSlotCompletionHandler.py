from typing import Dict, Any
from slot.SlotHandler import SlotHandler

class MissingSlotCompletionHandler(SlotHandler):
    """缺失槽位补全处理器"""

    def __init__(self, builder, next_handler=None):
        super().__init__(next_handler)
        self.builder = builder

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 补全缺失的槽位
        self.builder._complete_missing_slots(context['slots'], context.get('played_games', []))
        return super().handle(context)