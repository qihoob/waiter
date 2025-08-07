# E:\work\waiter\slot\UserDataSlotHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
from database.DB import get_user_order_history, get_user_played_games
import logging

logger = logging.getLogger(__name__)

class UserDataSlotHandler(SlotHandler):
    """用户数据槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get('user_id')
        if not user_id:
            return super().handle(context)

        try:
            # 获取用户历史数据
            order_history, played_games = self._get_user_data(user_id)
            context['order_history'] = order_history
            context['played_games'] = played_games

            # 将部分用户数据添加到槽位中
            if 'slots' not in context:
                context['slots'] = {}
            context['slots']['历史订单'] = order_history

            logger.info(f"获取到用户数据: {len(order_history)} 个历史订单, {len(played_games)} 个游戏")
        except Exception as e:
            logger.warning(f"获取用户数据失败: {e}")
            context['order_history'] = []
            context['played_games'] = []

        return super().handle(context)

    def _get_user_data(self, user_id):
        """获取用户数据

        Args:
            user_id: 用户ID

        Returns:
            tuple: (订单历史, 玩过的游戏)
        """
        if not user_id:
            return [], []

        try:
            return get_user_order_history(user_id), get_user_played_games(user_id)
        except Exception as e:
            logger.warning(f"获取用户数据失败: {e}")
            return [], []
