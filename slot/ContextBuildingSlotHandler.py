from typing import Dict, Any
from slot.SlotHandler import SlotHandler

class ContextBuildingSlotHandler(SlotHandler):
    """上下文构建槽位处理器"""

    def __init__(self, builder, next_handler=None):
        super().__init__(next_handler)
        self.builder = builder

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 构建模板上下文
        context['context_dict'] = self.builder._build_context(
            slots=context.get('slots', {}),
            location=context.get('location', '北京'),
            weather_info=context.get('weather', {}),
            order_history=context.get('order_history', []),
            played_games=context.get('played_games', []),
            user_request=context.get('input_text', '')
        )
        context['language'] = context.get('kwargs', {}).get("language", self.builder.default_language)
        return super().handle(context)