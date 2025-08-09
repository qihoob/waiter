# E:\work\waiter\slot\ContextHistorySaveHandler.py
from typing import Dict, Any, List
from slot.SlotHandler import SlotHandler, SlotHandlerInterrupt
import logging
from memory.local_cache import GlobalCache
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextHistorySaveHandler(SlotHandler):
    """上下文历史保存处理器，在槽位校验失败时保存当前上下文状态"""

    def __init__(self, required_slots: List[str] = None, next_handler=None, cache_expire_time=300):
        """
        初始化上下文历史保存处理器

        Args:
            required_slots: 必需的槽位列表
            next_handler: 下一个处理器
            cache_expire_time: 缓存过期时间（秒），默认5分钟
        """
        super().__init__(next_handler)
        self.cache = GlobalCache.get_instance()
        self.cache_expire_time = cache_expire_time
        # 定义关键槽位，可以根据业务需求调整
        self.required_slots = required_slots or [
            "场景",
            "人数",
            "菜系",
            "口味"
        ]

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_id = context.get('user_id')
            session_id = context.get('session_id')

            # 检查必需的槽位是否都已填写
            slots = context.get('slots', {})
            missing_slots = self._validate_required_slots(slots)

            # 如果有缺失的槽位且有用户ID和会话ID，则保存上下文
            if missing_slots and user_id and session_id:
                # 保存当前上下文到缓存
                self._save_context_to_history(user_id, session_id, context)
                logger.info(f"已保存上下文历史，用户ID: {user_id}, 会话ID: {session_id}")

                # 设置提示信息
                context['missing_slots'] = missing_slots
                context['need_user_input'] = True
                context['prompt_message'] = self._generate_prompt_message(missing_slots)

                # 中断处理链，等待用户补充信息
                raise SlotHandlerInterrupt(context)

        except SlotHandlerInterrupt:
            # 重新抛出中断异常
            raise
        except Exception as e:
            logger.error(f"保存上下文历史时出错: {e}")

        # 继续处理链
        return super().handle(context)

    def _validate_required_slots(self, slots: Dict[str, Any]) -> List[str]:
        """
        验证必需的槽位是否存在

        Args:
            slots: 已提取的槽位字典

        Returns:
            List[str]: 缺失的槽位列表
        """
        missing_slots = []

        for slot_name in self.required_slots:
            # 检查槽位是否存在且不为空
            if slot_name not in slots or not slots[slot_name]:
                missing_slots.append(slot_name)

        return missing_slots

    def _save_context_to_history(self, user_id: str, session_id: str, context: Dict[str, Any]):
        """
        将当前上下文保存到历史记录中

        Args:
            user_id: 用户ID
            session_id: 会话ID
            context: 当前上下文
        """
        try:
            cache_key = f"context_history:{user_id}:{session_id}"

            # 过滤需要保存的上下文字段
            context_to_save = {
                'slots': context.get('slots', {}),
                'location': context.get('location'),
                'location_info': context.get('location_info'),
                'weather_info': context.get('weather_info'),
                'order_history': context.get('order_history', []),
                'played_games': context.get('played_games', []),
                'input_text': context.get('input_text'),
                'is_order': context.get('is_order', False),
                'intent': context.get('intent'),
                'timestamp': datetime.now().timestamp()
            }

            # 保存到缓存
            self.cache.set(cache_key, context_to_save, self.cache_expire_time)
        except Exception as e:
            logger.warning(f"保存上下文历史失败: {e}")

    def _generate_prompt_message(self, missing_slots: List[str]) -> str:
        """
        生成提示用户输入的消息

        Args:
            missing_slots: 缺失的槽位列表

        Returns:
            str: 提示消息
        """
        slot_prompts = {
            "场景": "请问您是在什么场景下用餐？(例如: 朋友聚会、家庭聚餐、商务宴请等)",
            "人数": "请问有多少人用餐？",
            "菜系": "您想吃什么菜系？(例如: 川菜、粤菜、日料等)",
            "口味": "您偏好什么口味？(例如: 辣味、清淡、酸甜等)"
        }

        messages = [slot_prompts.get(slot, f"请提供{slot}信息") for slot in missing_slots]
        return messages
