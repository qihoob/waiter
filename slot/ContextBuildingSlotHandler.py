# E:\work\waiter\slot\ContextBuildingSlotHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import logging

logger = logging.getLogger(__name__)

class ContextBuildingSlotHandler(SlotHandler):
    """上下文构建槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 构建模板上下文
            context['context_dict'] = self._build_context(context)
            context['language'] = context.get('kwargs', {}).get("language", 'zh-CN')

            logger.info("上下文构建完成")
        except Exception as e:
            logger.error(f"上下文构建失败: {e}")
            context['context_dict'] = {}
            context['language'] = 'zh-CN'

        return super().handle(context)

    def _build_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """构建模板上下文字典

        Args:
            context: 处理上下文

        Returns:
            dict: 包含模板所需变量的上下文字典
        """
        slots = context.get('slots', {})
        location = context.get('location', '北京')
        weather_info = context.get('weather_info', {})
        order_history = context.get('order_history', [])
        played_games = context.get('played_games', [])
        user_request = context.get('input_text', '')
        is_order = context.get('is_order', False)

        try:
            context_dict = {
                "user_request": user_request,
                "city": location,

                # 用户画像分析字段
                "scene": slots.get("场景"),
                "people_count": slots.get("人数"),
                "cuisine": slots.get("菜系"),
                "taste": slots.get("口味"),
                "drink": slots.get("饮品"),
                "environment": slots.get("就餐环境"),
                "meal_type": slots.get("就餐形式"),

                # 健康与饮食限制字段
                "health_preference": slots.get("健康偏好"),
                "dietary_restriction": slots.get("忌口"),
                "allergy_avoidance": slots.get("过敏原"),

                # 外部条件影响字段
                "weather": slots.get("天气") or weather_info.get("天气", "未知"),
                "special_event": slots.get("特殊节日"),

                # 历史数据
                "conversation_history": "",  # 如果有对话历史可传入
                "order_history": "\n".join(order_history) if order_history else "无",

                # 地方特色菜品
                "local_dishes": self._get_local_dishes(location, slots.get("菜系")),
            }

            # 添加所有其他槽位作为备用
            for k, v in slots.items():
                if k not in context_dict:
                    context_dict[k] = v

            return context_dict

        except Exception as e:
            logger.error(f"构建上下文时发生错误: {e}")
            return {}

    def _get_local_dishes(self, location, cuisine=None):
        """获取当前城市的特色菜品

        Args:
            location: 城市名称
            cuisine: 菜系类型（可选）

        Returns:
            str: 特色菜品字符串
        """
        city_dishes_map = {
            "北京": ["烤鸭", "炸酱面", "涮羊肉"],
            "成都": ["火锅", "夫妻肺片", "担担面"],
            "广州": ["早茶", "烧味", "白切鸡"],
            "上海": ["小笼包", "红烧肉", "腌笃鲜"],
            "杭州": ["西湖醋鱼", "龙井虾仁", "东坡肉"]
        }

        dishes = city_dishes_map.get(location, ["地方特色菜"])

        if cuisine:
            cuisine_based_map = {
                "川菜": ["麻辣香锅", "水煮鱼", "麻婆豆腐"],
                "粤菜": ["烧味", "白切鸡", "早茶"],
                "本帮菜": ["红烧肉", "腌笃鲜", "油爆虾"],
                "日料": ["寿司", "刺身", "味噌汤"]
            }
            dishes = cuisine_based_map.get(cuisine, dishes)

        return ", ".join(dishes)
