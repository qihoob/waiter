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

# 本地缓存实例和过期时间
_location_cache = GlobalCache.get_instance()
CACHE_EXPIRE_TIME = 1800  # 30分钟缓存

class WeatherSlotHandler(SlotHandler):
    """天气信息槽位处理器"""

    def __init__(self,  next_handler=None):
        """
        初始化天气信息处理器

        Args:
            api_key: 天气API密钥
            next_handler: 下一个处理器
        """
        super().__init__(next_handler)
        self.api_key = ""  # 在实际使用中可以通过配置文件或环境变量设置API密钥

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 从上下文的槽位中获取城市信息
        location = context['slots'].get('city') if 'slots' in context else None

        # 将天气信息添加到槽位中
        if 'slots' not in context:
            context['slots'] = {}

        weather_info = self._get_weather(location)
        context['slots']['weather'] = weather_info.get('天气')
        context['weather_info'] = weather_info

        return super().handle(context)

    def _get_weather(self, location: str) -> Dict[str, Any]:
        """
        从网络获取天气信息

        Args:
            location: 城市名称

        Returns:
            dict: 天气信息
        """
        # 1. 先检查本地缓存
        cached_weather = self._get_weather_from_cache(location)
        if cached_weather:
            logger.info(f"从缓存获取 {location} 的天气信息")
            return cached_weather

        # 2. 缓存未命中，从网络获取
        try:
            weather_data = self._fetch_weather_from_api(location)
            if weather_data:
                # 保存到缓存
                self._save_weather_to_cache(location, weather_data)
                logger.info(f"从网络获取 {location} 的天气信息成功")
                return weather_data
        except Exception as e:
            logger.warning(f"从网络获取 {location} 的天气信息失败: {e}")

        # 3. 获取失败，返回默认值
        return {"天气": "未知", "温度": "未知", "湿度": "未知"}

    def _get_weather_from_cache(self, location: str) -> Dict[str, Any] | None:
        """
        从本地缓存获取天气信息

        Args:
            location: 城市名称

        Returns:
            dict | None: 天气信息，如果未找到或过期返回None
        """
        cache_key = f"weather:{location}"

        try:
            # 使用全局缓存的get方法
            cached_data = _location_cache.get(cache_key)
            return cached_data
        except Exception as e:
            logger.warning(f"从缓存获取天气信息失败: {e}")

        return None

    def _save_weather_to_cache(self, location: str, weather_data: Dict[str, Any]):
        """
        将天气信息保存到本地缓存

        Args:
            location: 城市名称
            weather_data: 天气数据
        """
        cache_key = f"weather:{location}"
        try:
            # 使用全局缓存的set方法
            _location_cache.set(cache_key, weather_data, CACHE_EXPIRE_TIME)
        except Exception as e:
            logger.warning(f"保存天气信息到缓存失败: {e}")

    def _fetch_weather_from_api(self, location: str) -> Dict[str, Any] | None:
        """
        从天气API获取天气信息

        Args:
            location: 城市名称

        Returns:
            dict | None: 天气信息
        """
        if not self.api_key:
            logger.warning("未配置天气API密钥")
            return None

        try:
            # 构建请求参数
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'zh_cn'
            }

            # 发送API请求
            response = requests.get("http://api.openweathermap.org/data/2.5/weather", params=params, timeout=5)
            response.raise_for_status()

            # 解析响应数据
            data = response.json()

            # 提取需要的天气信息
            weather_info = {
                "天气": data.get("weather", [{}])[0].get("description", "未知"),
                "温度": f"{data.get('main', {}).get('temp', '未知')}°C",
                "湿度": f"{data.get('main', {}).get('humidity', '未知')}%",
                "城市": data.get("name", location),
                "国家": data.get("sys", {}).get("country", "未知")
            }

            return weather_info

        except requests.exceptions.RequestException as e:
            logger.warning(f"天气API请求失败: {e}")
        except json.JSONDecodeError as e:
            logger.warning(f"解析天气API响应失败: {e}")
        except Exception as e:
            logger.warning(f"获取天气信息时发生未知错误: {e}")

        return None
