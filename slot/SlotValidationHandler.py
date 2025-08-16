# SlotValidationHandler.py (优化版)
from typing import Dict, Any, List, Set
from slot.SlotHandler import SlotHandler
import logging
from slot.context_manager import get_context_manager
# 导入统一的意图槽位映射定义
from slot.slot_definitions import INTENT_REQUIRED_SLOTS

logger = logging.getLogger(__name__)

class SlotValidationHandler(SlotHandler):
    """优化的槽位验证处理器，根据意图检查相应的槽位是否已填写"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

        # 使用统一的意图槽位映射定义
        self.intent_required_slots = INTENT_REQUIRED_SLOTS

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 使用ContextManager确保数据一致性
            ctx_manager = get_context_manager()
            ctx_manager.update_context(context)

            slots = ctx_manager.context.get('recognition', {}).get('slots', {})

            # 获取意图和该意图需要的槽位
            intent = ctx_manager.context.get('recognition', {}).get('intent', 'default')
            required_slots = self._get_required_slots_for_intent(intent)

            # 检查缺失的关键槽位
            missing_slots = self._validate_required_slots(slots, required_slots)

            if missing_slots:
                # 如果有缺失的槽位，设置提示信息
                context_updates = {
                    'processing': {
                        'missing_slots': missing_slots,
                        'need_user_input': True,
                        'prompt_message': self._generate_prompt_message(missing_slots, intent)
                    }
                }
                ctx_manager.update_context(context_updates)

                logger.info(f"意图 '{intent}' 需要槽位 {required_slots}，缺失槽位: {missing_slots}")
            else:
                # 所有关键槽位都已填写
                ctx_manager.update_context({
                    'processing': {
                        'need_user_input': False
                    }
                })

            # 同步回原始context
            context.update(ctx_manager.context['processing'])

        except Exception as e:
            logger.error(f"槽位验证过程中出错: {e}")

        return super().handle(context)

    def _get_required_slots_for_intent(self, intent: str) -> Set[str]:
        """根据意图获取需要的槽位集合"""
        # 精确匹配意图
        if intent in self.intent_required_slots:
            return self.intent_required_slots[intent].copy()

        # 模糊匹配意图（前缀匹配）
        for intent_prefix, slots in self.intent_required_slots.items():
            if intent.startswith(intent_prefix):
                return slots.copy()

        # 返回默认槽位
        return self.intent_required_slots.get("default", set()).copy()

    def _validate_required_slots(self, slots: Dict[str, Any], required_slots: Set[str]) -> List[str]:
        """验证必需的槽位是否存在"""
        # 使用SlotManager的统一验证逻辑
        from slot.ContextManager import get_context_manager
        ctx_manager = get_context_manager()
        return ctx_manager.slot_manager.validate_required_slots(slots, required_slots)

    def _generate_prompt_message(self, missing_slots: List[str], intent: str) -> str:
        """
        生成提示用户输入缺失信息的消息

        Args:
            missing_slots: 缺失的槽位列表
            intent: 当前意图

        Returns:
            str: 提示消息
        """
        slot_descriptions = {
            "人数": "用餐人数",
            "场景": "用餐场景",
            "菜系": "偏好菜系",
            "口味": "口味偏好",
            "健康偏好": "健康需求",
            "忌口": "忌口食物",
            "过敏原": "过敏食物",
            "饮品": "饮品偏好",
            "节日": "节日信息",
            "游戏": "游戏偏好"
        }

        # 根据意图定制提示消息
        intent_prompts = {
            "order_food": "您想预订餐厅，请提供",
            "recommend_dish": "您想获取菜品推荐，请提供",
            "query_nutrition": "您想了解营养信息，请提供",
            "recommend_game": "您想获取游戏推荐，请提供",
            "play_game": "您想玩游戏，请提供",
            "order_drink": "您想预订饮品，请提供",
            "recommend_drink": "您想获取饮品推荐，请提供",
            "festival_recommend": "您想获取节日推荐，请提供"
        }

        # 构建提示消息
        prompt_prefix = intent_prompts.get(intent, "为了更好地为您服务，请提供")
        missing_descriptions = [slot_descriptions.get(slot, slot) for slot in missing_slots]
        
        if len(missing_descriptions) == 1:
            return f"{prompt_prefix}{missing_descriptions[0]}"
        else:
            descriptions_str = "、".join(missing_descriptions[:-1]) + f"和{missing_descriptions[-1]}"
            return f"{prompt_prefix}{descriptions_str}"
