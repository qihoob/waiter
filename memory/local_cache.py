from typing import Dict, Any
import json
import logging
import time

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GlobalCache:
    """全局缓存管理器"""

    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalCache, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls):
        """
        获取GlobalCache单例实例的标准方法

        Returns:
            GlobalCache: GlobalCache单例实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get(self, key: str) -> Any:
        """获取缓存值"""
        if key not in self._cache:
            return None

        try:
            cached_data = self._cache[key]
            cached_value = cached_data.get('value')
            timestamp = cached_data.get('timestamp', 0)
            expire_time = cached_data.get('expire_time', 300)  # 默认5分钟

            # 检查是否过期
            if time.time() - timestamp > expire_time:
                # 缓存过期，删除该条目
                del self._cache[key]
                return None

            return cached_value
        except Exception as e:
            logger.warning(f"从全局缓存获取值失败: {e}")
            return None

    def set(self, key: str, value: Any, expire_time: int = 300):
        """设置缓存值"""
        try:
            self._cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'expire_time': expire_time
            }
        except Exception as e:
            logger.warning(f"保存值到全局缓存失败: {e}")

    def delete(self, key: str):
        """删除缓存值"""
        if key in self._cache:
            del self._cache[key]

    def clear(self):
        """清空缓存"""
        self._cache.clear()

    def size(self):
        """获取缓存大小"""
        return len(self._cache)

    def keys(self):
        """获取所有缓存键"""
        return list(self._cache.keys())

    def exists(self, key: str) -> bool:
        """检查键是否存在且未过期"""
        return self.get(key) is not None


# 创建全局缓存实例的便捷函数
def get_global_cache() -> GlobalCache:
    """
    获取全局缓存实例的便捷函数

    Returns:
        GlobalCache: GlobalCache单例实例
    """
    return GlobalCache.get_instance()
