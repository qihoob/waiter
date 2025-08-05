from typing import Dict, Any
from slot.SlotHandler import SlotHandler

class TemplateSelectionSlotHandler(SlotHandler):
    """模板选择槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 根据意图选择模板
        context['template_name'] = self.builder._select_template(
            context.get('kwargs', {}),
            context.get('intent')
        )
        return super().handle(context)