# E:\work\waiter\slot\LocationSlotHandler.py
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
        # 检查是否需要处理位置信息
        # 只有在有实际点餐意图且包含关键点餐信息时才处理位置
        if self._should_process_location(context):
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

    def _should_process_location(self, context: Dict[str, Any]) -> bool:
        """
        判断是否需要处理位置信息
        
        Args:
            context: 处理上下文
            
        Returns:
            bool: 是否需要处理位置信息
        """
        # 检查是否有点餐意图
        is_order = context.get('is_order', False)
        if not is_order:
            return False

        # 检查是否包含关键点餐信息
        slots = context.get('slots', {})

        # 如果只有饮品信息，不需要处理位置
        only_drink = (
                slots.get('饮品') and
                not slots.get('菜系') and
                not slots.get('口味') and
                not slots.get('就餐形式') and
                not slots.get('健康偏好') and
                not slots.get('人数') and
                not slots.get('场景')
        )

        # 如果只有饮品信息，不处理位置
        if only_drink:
            return False

        # 其他情况下，如果有任何关键点餐信息就需要处理位置
        has_key_info = (
                slots.get('菜系') or
                slots.get('口味') or
                slots.get('就餐形式') or
                slots.get('健康偏好') or
                slots.get('人数') or
                slots.get('场景')
        )

        return bool(has_key_info)

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
        try:
            # 使用GlobalCache的get方法而不是直接访问
            cached_data = _location_cache.get(cache_key)
            if cached_data is None:
                return None

            location_info = cached_data.get('data')
            timestamp = cached_data.get('timestamp', 0)

            # 检查是否过期
            if datetime.now().timestamp() - timestamp > self.cache_expire_time:
                # 缓存过期，删除该条目
                _location_cache.delete(cache_key)
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
            _location_cache.set(cache_key, {
                'data': location_data,
                'timestamp': datetime.now().timestamp()
            }, self.cache_expire_time)
        except Exception as e:
            logger.warning(f"保存位置信息到缓存失败: {e}")


# 测试代码
def test_location_slot_handler():
    """测试位置槽位处理器"""
    print("=" * 50)
    print("测试位置槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = LocationSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "无点餐意图",
            "context": {
                "is_order": False,
                "cleaned_text": "你好，我想了解一下你们的菜品"
            }
        },
        {
            "name": "只有饮品信息",
            "context": {
                "is_order": True,
                "cleaned_text": "我要一杯可口可乐",
                "slots": {
                    "饮品": "可口可乐"
                }
            }
        },
        {
            "name": "有菜系信息",
            "context": {
                "is_order": True,
                "cleaned_text": "我想吃川菜",
                "slots": {
                    "菜系": "川菜"
                }
            }
        },
        {
            "name": "有口味信息",
            "context": {
                "is_order": True,
                "cleaned_text": "我想要辣一点的菜",
                "slots": {
                    "口味": "辣味"
                }
            }
        },
        {
            "name": "有场景信息",
            "context": {
                "is_order": True,
                "cleaned_text": "朋友聚会吃饭",
                "slots": {
                    "场景": "朋友聚会"
                }
            }
        },
        {
            "name": "有饮品和菜系信息",
            "context": {
                "is_order": True,
                "cleaned_text": "我要一杯啤酒和川菜",
                "slots": {
                    "饮品": "啤酒",
                    "菜系": "川菜"
                }
            }
        },
        {
            "name": "已有位置信息",
            "context": {
                "is_order": True,
                "location": "上海",
                "cleaned_text": "我想吃川菜",
                "slots": {
                    "菜系": "川菜"
                }
            }
        }
    ]

    # 执行测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"输入上下文: {test_case['context']}")

        try:
            # 执行处理
            result_context = handler.handle(test_case['context'].copy())

            # 输出结果
            location = result_context.get('location', '未获取到')
            location_info = result_context.get('location_info', '未获取到')
            slots = result_context.get('slots', {})
            city = slots.get('city', '未获取到')

            print(f"位置信息: {location}")
            print(f"详细位置信息: {location_info}")
            print(f"城市槽位: {city}")

            # 验证是否应该处理位置
            should_process = handler._should_process_location(test_case['context'])
            print(f"是否应该处理位置: {should_process}")

        except Exception as e:
            print(f"处理出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_location_slot_handler()
