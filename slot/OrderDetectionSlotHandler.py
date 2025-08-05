from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import logging
from prompt_builder.config import ORDER_KEYWORDS
from memory.local_cache import GlobalCache
import time

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 本地缓存字典
_local_cache =  GlobalCache.get_instance()
# 缓存过期时间（秒）
CACHE_EXPIRE_TIME = 300  # 5分钟

class OrderDetectionSlotHandler(SlotHandler):
    """订单检测槽位处理器"""

    def __init__(self,  next_handler=None):
        """
        初始化订单检测处理器
        
        Args:
            cache_expire_time: 缓存过期时间（秒），默认5分钟
            next_handler: 下一个处理器
        """
        super().__init__(next_handler)
        self.cache_expire_time = CACHE_EXPIRE_TIME

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        user_id = context.get('user_id')
        session_id = context.get('session_id')

        # 构建缓存键
        cache_key = f"user_order_status:{user_id}:{session_id}" if user_id and session_id else None

        # 1. 优先从本地缓存中获取订单状态
        is_order = self._get_order_status_from_cache(cache_key)

        if is_order is not None:
            # 如果缓存中有订单状态，直接使用缓存值
            context['is_order'] = is_order
            logger.info(f"从本地缓存获取订单状态: {is_order}")
        else:
            # 2. 如果没有缓存，从槽位中检测是否有下单意图
            context['is_order'] = (context.get('is_order', False) or
                                          self._detect_order_intent(context['tokenized_text']))

            # 3. 如果检测到下单意图，保存到本地缓存
            if context['is_order'] and cache_key:
                self._save_order_status_to_cache(cache_key, context['is_order'])
                logger.info(f"检测到下单意图，已保存到本地缓存: {context['is_order']}")

        return super().handle(context)

    def _get_order_status_from_cache(self, cache_key: str) -> bool | None:
        """
        从本地缓存中获取订单状态
        
        Args:
            cache_key: 缓存键
            
        Returns:
            bool | None: 订单状态，如果未找到或过期返回None
        """
        if not cache_key or cache_key not in _local_cache:
            return None

        try:
            cached_data = _local_cache[cache_key]
            cached_value = cached_data.get('value')
            timestamp = cached_data.get('timestamp', 0)

            # 检查是否过期
            if time.time() - timestamp > self.cache_expire_time:
                # 缓存过期，删除该条目
                del _local_cache[cache_key]
                return None

            return cached_value
        except Exception as e:
            logger.warning(f"从本地缓存获取订单状态失败: {e}")

        return None

    def _save_order_status_to_cache(self, cache_key: str, is_order: bool):
        """
        将订单状态保存到本地缓存
        
        Args:
            cache_key: 缓存键
            is_order: 订单状态
        """
        if not cache_key:
            return

        try:
            _local_cache[cache_key] = {
                'value': is_order,
                'timestamp': time.time()
            }
        except Exception as e:
            logger.warning(f"保存订单状态到本地缓存失败: {e}")

    def _detect_order_intent(self, tokenized_text):
        """
        检测用户是否有下单意图（使用已分词文本）
        
        Args:
            tokenized_text: 已分词的文本

        Returns:
            bool: 是否有下单意图
        """
        if not tokenized_text:
            return False

        # 使用可配置的下单意图词典
        return any(keyword in tokenized_text for keyword in ORDER_KEYWORDS)
