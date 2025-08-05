from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import requests
import json
import logging
from datetime import datetime
from memory.local_cache import GlobalCache

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 本地缓存字典和过期时间
# 本地缓存字典
_location_cache =  GlobalCache.get_instance()
CACHE_EXPIRE_TIME = 1800  # 30分钟缓存

class LocationSlotHandler(SlotHandler):
    """位置信息槽位处理器"""

    def __init__(self,  next_handler=None):
        """
        初始化位置信息处理器

        Args:
            cache_expire_time: 缓存过期时间（秒），默认30分钟
            next_handler: 下一个处理器
        """
        super().__init__(next_handler)
        self.cache_expire_time = CACHE_EXPIRE_TIME

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 如果上下文中没有location，则根据IP获取位置信息
        if 'location' not in context or not context['location']:
            ip = context.get('ip')
            location_info = self._get_location_by_ip(ip)

            # 将位置信息添加到上下文中
            context['location_info'] = location_info
            context['location'] = location_info.get('city', '北京')

            # 同时将城市信息添加到槽位中
            if 'slots' not in context:
                context['slots'] = {}
            context['slots']['city'] = location_info.get('city')
            context['slots']['region'] = location_info.get('region')

        return super().handle(context)

    def _get_location_by_ip(self, ip: str = None) -> Dict[str, Any]:
        """
        根据IP地址获取位置信息（使用淘宝IP地址库）

        Args:
            ip: IP地址，如果为None则获取当前请求的IP

        Returns:
            dict: 位置信息
        """
        # 1. 先检查本地缓存
        cache_key = f"location:ip:{ip or 'current'}"
        cached_location = self._get_location_from_cache(cache_key)
        if cached_location:
            logger.info(f"从缓存获取IP {ip or 'current'} 的位置信息")
            return cached_location

        # 2. 缓存未命中，从淘宝API获取
        try:
            location_data = self._fetch_location_from_taobao(ip)
            if location_data:
                # 保存到缓存
                self._save_location_to_cache(cache_key, location_data)
                logger.info(f"从淘宝API获取IP {ip or 'current'} 的位置信息成功")
                return location_data
        except Exception as e:
            logger.warning(f"从淘宝API获取IP {ip or 'current'} 的位置信息失败: {e}")

        # 3. 获取失败，返回默认值
        return {
            "ip": ip or "unknown",
            "country": "中国",
            "region": "北京",
            "city": "北京",
            "isp": "unknown",
            "area": "未知"
        }

    def _fetch_location_from_taobao(self, ip: str = None) -> Dict[str, Any] | None:
        """
        从淘宝IP地址库获取位置信息

        Args:
            ip: IP地址

        Returns:
            dict | None: 位置信息
        """
        try:
            # 淘宝IP地址库API
            taobao_api_url = "http://ip.taobao.com/service/getIpInfo.php"

            # 构建请求参数
            params = {}
            if ip:
                params['ip'] = ip
            else:
                params['ip'] = 'myip'  # 淘宝API中使用myip表示当前请求的IP

            # 发送API请求
            response = requests.get(taobao_api_url, params=params, timeout=5)
            response.raise_for_status()

            # 解析响应数据
            data = response.json()

            # 检查返回码
            if data.get('code') != 0:
                logger.warning(f"淘宝IP地址库API返回错误: {data.get('data')}")
                return None

            # 提取需要的位置信息
            ip_info = data.get('data', {})
            location_info = {
                "ip": ip_info.get('ip', ip or 'unknown'),
                "country": ip_info.get('country', '未知'),
                "region": ip_info.get('region', '未知'),
                "city": ip_info.get('city', '未知'),
                "isp": ip_info.get('isp', '未知'),
                "area": ip_info.get('area', '未知')
            }

            return location_info

        except requests.exceptions.RequestException as e:
            logger.warning(f"淘宝IP地址库API请求失败: {e}")
        except json.JSONDecodeError as e:
            logger.warning(f"解析淘宝IP地址库API响应失败: {e}")
        except Exception as e:
            logger.warning(f"获取位置信息时发生未知错误: {e}")

        return None

    def _get_location_from_cache(self, cache_key: str) -> Dict[str, Any] | None:
        """
        从本地缓存获取位置信息

        Args:
            cache_key: 缓存键

        Returns:
            dict | None: 位置信息，如果未找到或过期返回None
        """
        if cache_key not in _location_cache:
            return None

        try:
            cached_data = _location_cache[cache_key]
            location_info = cached_data.get('data')
            timestamp = cached_data.get('timestamp', 0)

            # 检查是否过期
            if datetime.now().timestamp() - timestamp > self.cache_expire_time:
                # 缓存过期，删除该条目
                del _location_cache[cache_key]
                return None

            return location_info
        except Exception as e:
            logger.warning(f"从缓存获取位置信息失败: {e}")

        return None

    def _save_location_to_cache(self, cache_key: str, location_data: Dict[str, Any]):
        """
        将位置信息保存到本地缓存

        Args:
            cache_key: 缓存键
            location_data: 位置数据
        """
        try:
            _location_cache[cache_key] = {
                'data': location_data,
                'timestamp': datetime.now().timestamp()
            }
        except Exception as e:
            logger.warning(f"保存位置信息到缓存失败: {e}")
