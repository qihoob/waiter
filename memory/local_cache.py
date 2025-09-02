import os
import json
import logging
import time
import threading
from typing import Dict, Any, Optional
from collections import OrderedDict

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, capacity: int = 1000):
        # 添加容量上限检查，防止过大的缓存占用过多内存
        if capacity <= 0 or capacity > 100000:
            raise ValueError("缓存容量必须在1-100000之间")
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Any:
        """获取缓存值"""
        with self.lock:
            if key not in self.cache:
                return None
                
            # 移动到末尾表示最近使用
            self.cache.move_to_end(key)
            return self.cache[key]
            
    def put(self, key: str, value: Any, expire_time: int = 300) -> None:
        """设置缓存值"""
        # 添加过期时间限制，防止过长的缓存时间
        if expire_time <= 0 or expire_time > 86400:  # 最大24小时
            expire_time = 300  # 使用默认值
            
        with self.lock:
            if key in self.cache:
                # 更新现有键值
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.capacity:
                # 移除最久未使用的项
                self.cache.popitem(last=False)
                
            # 存储值和过期时间
            self.cache[key] = {
                'value': value,
                'timestamp': time.time(),
                'expire_time': expire_time
            }
            
    def delete(self, key: str) -> None:
        """删除缓存值"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                
    def clear(self) -> None:
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            
    def size(self) -> int:
        """获取缓存大小"""
        with self.lock:
            return len(self.cache)
            
    def keys(self) -> list:
        """获取所有缓存键"""
        with self.lock:
            return list(self.cache.keys())
            
    def exists(self, key: str) -> bool:
        """检查键是否存在且未过期"""
        with self.lock:
            if key not in self.cache:
                return False
                
            cached_data = self.cache[key]
            timestamp = cached_data.get('timestamp', 0)
            expire_time = cached_data.get('expire_time', 300)
            
            # 检查是否过期
            if time.time() - timestamp > expire_time:
                # 缓存过期，删除该条目
                del self.cache[key]
                return False
                
            # 添加缓存项大小检查，防止过大的值占用内存
            value = cached_data.get('value')
            if value is not None:
                # 简单估算对象大小（以字节为单位）
                import sys
                size = sys.getsizeof(value)
                if size > 10 * 1024 * 1024:  # 超过10MB的单个缓存项
                    logger.warning(f"检测到过大的缓存项 ({size} bytes)，自动清理")
                    del self.cache[key]
                    return False
                    
            return True

class GlobalCache:
    """全局缓存管理器"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(GlobalCache, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化缓存"""
        try:
            self.cache = LRUCache(int(os.getenv("CACHE_CAPACITY", 1000)))
            logger.info("全局缓存管理器初始化完成")
        except Exception as e:
            logger.error(f"全局缓存管理器初始化失败: {e}")
            raise

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
        try:
            if not self.cache.exists(key):
                return None
                
            cached_data = self.cache.get(key)
            if cached_data is None:
                return None
                
            return cached_data.get('value')
        except Exception as e:
            logger.warning(f"从全局缓存获取值失败: {e}")
            return None

    def set(self, key: str, value: Any, expire_time: int = 300):
        """设置缓存值"""
        try:
            self.cache.put(key, value, expire_time)
        except Exception as e:
            logger.warning(f"保存值到全局缓存失败: {e}")

    def delete(self, key: str):
        """删除缓存值"""
        try:
            self.cache.delete(key)
        except Exception as e:
            logger.warning(f"删除缓存值失败: {e}")

    def clear(self):
        """清空缓存"""
        try:
            self.cache.clear()
        except Exception as e:
            logger.warning(f"清空缓存失败: {e}")

    def size(self):
        """获取缓存大小"""
        try:
            return self.cache.size()
        except Exception as e:
            logger.warning(f"获取缓存大小失败: {e}")
            return 0

    def keys(self):
        """获取所有缓存键"""
        try:
            return self.cache.keys()
        except Exception as e:
            logger.warning(f"获取缓存键列表失败: {e}")
            return []

    def exists(self, key: str) -> bool:
        """检查键是否存在且未过期"""
        try:
            return self.cache.exists(key)
        except Exception as e:
            logger.warning(f"检查缓存键存在性失败: {e}")
            return False

# 创建全局缓存实例的便捷函数
def get_global_cache() -> GlobalCache:
    """
    获取全局缓存实例的便捷函数

    Returns:
        GlobalCache: GlobalCache单例实例
    """
    try:
        return GlobalCache.get_instance()
    except Exception as e:
        logger.error(f"获取全局缓存实例失败: {e}")
        raise

# 全局缓存实例（可选）
# 注释掉自动初始化，避免在模块导入时就创建实例
# global_cache = GlobalCache.get_instance()
