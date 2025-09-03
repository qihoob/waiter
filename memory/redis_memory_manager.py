from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from typing import Dict
import redis


# === Redis Memory 管理器 ===
class RedisMemoryManager:
    def __init__(self, redis_url="redis://localhost:6379/1", ttl_seconds: int = 3600):
        self.redis_url = redis_url
        self.ttl_seconds = ttl_seconds
        self.redis_client = redis.from_url(redis_url, decode_responses=True)

    def get_memory(self, user_id: str, session_id: str) -> ConversationBufferMemory:
        session_key = f"user:{user_id}:session:{session_id}"
        chat_history = RedisChatMessageHistory(
            url=self.redis_url,
            session_id=session_key,
            ttl=self.ttl_seconds
        )
        memory = ConversationBufferMemory(
            chat_memory=chat_history,
            return_messages=True
        )
        return memory

    def clear_memory(self, user_id: str, session_id: str):
        session_key = f"user:{user_id}:session:{session_id}"
        self.redis_client.delete(session_key)


