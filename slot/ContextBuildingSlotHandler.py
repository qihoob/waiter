# ContextBuildingSlotHandler.py (优化版)
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import logging

logger = logging.getLogger(__name__)

class ContextBuildingSlotHandler(SlotHandler):
    """优化的上下文构建槽位处理器"""

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 构建模板上下文
            context_dict = self._build_context(context)

            # 更新context
            context['context_dict'] = context_dict
            context['language'] = context.get('kwargs', {}).get("language", 'zh-CN')

            logger.info("上下文构建完成")
        except Exception as e:
            logger.error(f"上下文构建失败: {e}")
            context['context_dict'] = {}
            context['language'] = 'zh-CN'

        return super().handle(context)

    def _build_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """构建模板上下文字典"""
        slots = context.get('recognition', {}).get('slots', {})
        location = context.get('environment', {}).get('location', '北京')
        weather_info = context.get('environment', {}).get('weather_info', {})
        order_history = context.get('history', {}).get('orders', [])
        user_request = context.get('input_text', context.get('input', {}).get('text', ''))
        is_order = context.get('recognition', {}).get('is_order', False)

        try:
            context_dict = {
                # 基础信息
                "user_request": user_request,
                "city": location,
                
                # 用户画像信息
                "people_count": slots.get("人数"),
                "scene": slots.get("场景"),
                "cuisine": slots.get("菜系"),
                "special_dish": slots.get("特色菜"),
                "taste": slots.get("口味"),
                "drink": slots.get("饮品"),
                "environment": slots.get("就餐环境"),
                "meal_type": slots.get("就餐形式"),
                
                # 菜系详细信息
                "cuisine_features": slots.get("菜系说明"),
                "flavor_features": slots.get("口味特点"),
                
                # 健康与饮食限制
                "health_preference": slots.get("健康偏好"),
                "dietary_restriction": slots.get("忌口"),
                "allergy_avoidance": slots.get("过敏原"),
                
                # 外部条件
                "weather": self._get_weather_info(slots, weather_info),
                "festival": slots.get("特殊节日") or slots.get("节日"),
                
                # 历史数据
                "order_history": self._format_order_history(order_history),
                "is_order_placed": is_order,
                
                # 地方特色
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

    def _get_weather_info(self, slots: Dict[str, Any], weather_info: Dict[str, Any]) -> str:
        """获取天气信息"""
        return (slots.get("天气状态") or 
                slots.get("天气") or 
                weather_info.get("天气", "未知"))

    def _format_order_history(self, order_history: list) -> str:
        """格式化订单历史"""
        return "\n".join(order_history) if order_history else "无"

    def _get_local_dishes(self, location: str, cuisine: str = None) -> str:
        """获取当前城市的特色菜品"""
        city_dishes_map = {
            "北京": ["烤鸭", "炸酱面", "涮羊肉"],
            "成都": ["火锅", "夫妻肺片", "担担面"],
            "广州": ["早茶", "烧味", "白切鸡"],
            "上海": ["小笼包", "红烧肉", "腌笃鲜"],
            "杭州": ["西湖醋鱼", "龙井虾仁", "东坡肉"]
        }

        dishes = city_dishes_map.get(location, [])
        
        if cuisine:
            cuisine_based_map = {
                "川菜": ["麻辣香锅", "水煮鱼", "麻婆豆腐"],
                "粤菜": ["烧味", "白切鸡", "早茶"],
                "本帮菜": ["红烧肉", "腌笃鲜", "油爆虾"],
                "日料": ["寿司", "刺身", "味噌汤"]
            }
            dishes = cuisine_based_map.get(cuisine, dishes)

        return ", ".join(dishes) if dishes else ""
