from typing import Dict, Any
from slot.SlotHandler import SlotHandler

class GameRecommendationSlotHandler(SlotHandler):
    """游戏推荐槽位处理器"""

    def __init__(self,  next_handler=None):
        super().__init__(next_handler)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 如果已下单，生成游戏推荐
        if context.get('is_order'):
            context['intent'] = "game_recommendation"
        return super().handle(context)