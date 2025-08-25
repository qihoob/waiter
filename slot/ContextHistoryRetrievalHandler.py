# E:\work\waiter\slot\ContextHistoryRetrievalHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import logging
from memory.local_cache import GlobalCache
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextHistoryRetrievalHandler(SlotHandler):
    """上下文历史检索处理器，从缓存中获取历史上下文"""

    def __init__(self, next_handler=None, cache_expire_time=300):
        """
        初始化上下文历史检索处理器

        Args:
            next_handler: 下一个处理器
            cache_expire_time: 缓存过期时间（秒），默认5分钟
        """
        super().__init__(next_handler)
        self.cache = GlobalCache.get_instance()
        self.cache_expire_time = cache_expire_time

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_id = context.get('user_id')

            # 尝试从历史中恢复上下文
            if user_id:
                historical_context = self._get_context_from_history(user_id)
                if historical_context:
                    # 合并历史上下文和当前上下文
                    merged_context = self._merge_context(historical_context, context)
                    context.update(merged_context)
                    logger.info(f"已从历史恢复上下文，用户ID: {user_id}")

        except Exception as e:
            logger.error(f"检索上下文历史时出错: {e}")

        return super().handle(context)

    def _get_context_from_history(self, user_id: str) -> Dict[str, Any]:
        """
        从历史记录中获取上下文

        Args:
            user_id: 用户ID

        Returns:
            Dict[str, Any]: 历史上下文，如果不存在或过期则返回空字典
        """
        try:
            # 获取槽位信息和输入历史
            slots_cache_key = f"context_slots:{user_id}"
            input_cache_key = f"context_input:{user_id}"
            
            # 获取历史槽位和输入信息
            cached_slots = self.cache.get(slots_cache_key) or {}
            cached_input_history = self.cache.get(input_cache_key) or []
            
            # 检查是否过期（只需要检查一个，因为它们同时创建）
            # 这里简化处理，实际应用中可能需要更复杂的过期检查
            
            # 构建历史上下文
            historical_context = {}
            
            # 添加槽位信息
            if cached_slots:
                historical_context['slots'] = cached_slots
                
            # 合并输入历史，用逗号连接，且历史在前
            if cached_input_history:
                historical_context['input_text'] = "，".join(cached_input_history)
                
            return historical_context

        except Exception as e:
            logger.warning(f"获取上下文历史失败: {e}")

        return {}

    def _merge_context(self, historical_context: Dict[str, Any], current_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并历史上下文和当前上下文

        Args:
            historical_context: 历史上下文
            current_context: 当前上下文

        Returns:
            Dict[str, Any]: 合并后的上下文
        """
        merged_context = historical_context.copy()

        # 更新当前上下文中的新信息
        for key, value in current_context.items():
            # 特别处理槽位信息的合并
            if key == 'slots' and 'slots' in merged_context:
                # 合并槽位，当前的优先级更高
                merged_slots = merged_context['slots'].copy()
                merged_slots.update(value)
                merged_context['slots'] = merged_slots
            # 特别处理输入文本，历史在前，新的在后
            elif key == 'input_text' and 'input_text' in merged_context:
                # 历史输入在前，当前输入在后，用逗号连接
                merged_context['input_text'] = f"{merged_context['input_text']}，{value}"
            else:
                # 其他字段直接更新为当前值
                merged_context[key] = value

        return merged_context
