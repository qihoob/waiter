from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory
from typing import Dict
import redis


class RedisMemoryManager:
    def __init__(self, redis_url="redis://localhost:6379", ttl_seconds: int = 3600):
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds  # 可选：设置会话超时时间
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

    def get_memory(self, user_id: str, session_id: str) -> ConversationBufferMemory:
        """
        获取用户指定会话的 memory 实例（自动从 Redis 读取历史）
        """
        session_key = f"user:{user_id}:session:{session_id}"

        # RedisChatMessageHistory 自动读取 & 存储对话记录
        chat_history = RedisChatMessageHistory(
            url=self.redis_url,
            session_id=session_key,
            ttl=self.ttl_seconds  # 会话多久自动过期
        )

        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            return_messages=True  # 用 message 对象而不是纯字符串
        )

        return memory

    def clear_memory(self, user_id: str, session_id: str):
        """
        清除某用户某会话的历史记录（如点餐完成后清空）
        """
        session_key = f"user:{user_id}:session:{session_id}"
        self.redis_client.delete(session_key)
