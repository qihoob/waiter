# ContextBuildingSlotHandler.py (优化版)
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import logging
from slot.ContextManager import get_context_manager

logger = logging.getLogger(__name__)

class ContextBuildingSlotHandler(SlotHandler):
    """优化的上下文构建槽位处理器"""

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 使用ContextManager确保数据一致性
            ctx_manager = get_context_manager()
            ctx_manager.update_context(context)

            # 构建模板上下文
            context_dict = self._build_context(ctx_manager.context)

            # 更新context
            context_updates = {
                'output': {
                    'context_dict': context_dict,
                    'language': context.get('kwargs', {}).get("language", 'zh-CN')
                }
            }
            ctx_manager.update_context(context_updates)

            # 同步回原始context
            context.update({
                'context_dict': context_dict,
                'language': ctx_manager.context['output']['language']
            })

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
        played_games = context.get('history', {}).get('games', [])
        user_request = context.get('input', {}).get('text', '')
        is_order = context.get('recognition', {}).get('is_order', False)

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
                "is_order_placed": is_order,

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
        """获取当前城市的特色菜品"""
        # 这里可以实现具体的逻辑来获取地方特色菜品
        # 暂时返回空列表作为示例
        return []
