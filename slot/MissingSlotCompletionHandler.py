# E:\work\waiter\slot\MissingSlotCompletionHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import logging

logger = logging.getLogger(__name__)

class MissingSlotCompletionHandler(SlotHandler):
    """缺失槽位补全处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            slots = context.get('slots', {})
            played_games = context.get('played_games', [])

            # 补全缺失的槽位
            self._complete_missing_slots(slots, played_games)
            context['slots'] = slots

            logger.info(f"补全后的槽位: {slots}")
        except Exception as e:
            logger.warning(f"槽位补全失败: {e}")

        return super().handle(context)

    def _complete_missing_slots(self, slots, played_games):
        """补全缺失槽位

        Args:
            slots: 提取的槽位字典
            played_games: 玩过的游戏列表
        """
        try:
            # 补全人数槽位
            if "人数" not in slots:
                if "场景" in slots and "朋友聚会" in slots.get("场景", ""):
                    slots["人数"] = len(played_games) + 1 if played_games else 4
                else:
                    # 默认2人
                    slots["人数"] = 2

            # 补全城市槽位
            if "city" not in slots and "location" in slots:
                slots["city"] = slots["location"]
            elif "city" not in slots:
                slots["city"] = "北京"

        except Exception as e:
            logger.warning(f"补全槽位时出错: {e}")
