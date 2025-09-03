# E:\work\waiter\slot\ContextHistorySaveHandler.py
from typing import Dict, Any, List, Set
from slot.SlotHandler import SlotHandler, SlotHandlerInterrupt
import logging
from memory.local_cache import GlobalCache
from datetime import datetime
# 导入统一的意图槽位映射定义
from slot.slot_definitions import INTENT_REQUIRED_SLOTS

logger = logging.getLogger(__name__)

class ContextHistorySaveHandler(SlotHandler):
    """上下文验证和历史保存处理器，根据意图验证槽位并在缺失时保存上下文"""

    def __init__(self, next_handler=None, cache_expire_time=300):
        """
        初始化上下文验证和历史保存处理器

        Args:
            next_handler: 下一个处理器
            cache_expire_time: 缓存过期时间（秒），默认5分钟
        """
        super().__init__(next_handler)
        self.cache = GlobalCache.get_instance()
        self.cache_expire_time = cache_expire_time

        # 使用统一的意图槽位映射定义
        self.intent_required_slots = INTENT_REQUIRED_SLOTS

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_id = context.get('user_id')
            session_id = context.get('session_id')

            slots = context.get('slots', {})

            # 获取意图和该意图需要的槽位
            intent = context.get('intent') or 'default'  # 确保intent不为None
            required_slots = self._get_required_slots_for_intent(intent)

            # 检查缺失的关键槽位
            missing_slots = self._validate_required_slots(slots, required_slots)

            # 如果有缺失的槽位且有用户ID和会话ID，则保存上下文
            if missing_slots:
                # 保存当前上下文到缓存
                self._save_context_to_history(user_id,  context)
                #logger.info(f"已保存上下文历史，用户ID: {user_id}, 会话ID: {session_id}")

                # 设置提示信息
                context['missing_slots'] = missing_slots
                context['need_user_input'] = True
                context['prompt_message'] = self._generate_prompt_message(missing_slots, intent)

                # 中断处理链，等待用户补充信息
                raise SlotHandlerInterrupt(context)
            elif not missing_slots:
                # 所有关键槽位都已填写
                context['need_user_input'] = False

        except SlotHandlerInterrupt:
            # 重新抛出中断异常
            logger.info("槽位验证中断，等待用户输入缺失信息")
            raise
        except Exception as e:
            logger.error(f"上下文验证和历史保存时出错: {e}")

        # 继续处理链
        return super().handle(context)

    def _get_required_slots_for_intent(self, intent: str) -> Set[str]:
        """
        根据意图获取需要的槽位集合

        Args:
            intent: 用户意图

        Returns:
            Set[str]: 需要的槽位集合
        """
        # 确保intent不为None
        if not intent:
            intent = 'default'

        # 精确匹配意图
        if intent in self.intent_required_slots:
            return self.intent_required_slots[intent].copy()

        # 模糊匹配意图（前缀匹配）
        for intent_prefix, slots in self.intent_required_slots.items():
            # 确保intent_prefix不为None后再进行比较
            if intent_prefix and intent.startswith(intent_prefix):
                return slots.copy()

        # 返回默认槽位
        return self.intent_required_slots.get("default", set()).copy()

    def _validate_required_slots(self, slots: Dict[str, Any], required_slots: Set[str]) -> List[str]:
        """
        验证必需的槽位是否存在

        Args:
            slots: 已提取的槽位字典
            required_slots: 当前意图需要的槽位集合

        Returns:
            List[str]: 缺失的槽位列表
        """
        missing_slots = []

        for slot_name in required_slots:
            # 检查槽位是否存在且不为空
            if slot_name not in slots or not slots[slot_name]:
                missing_slots.append(slot_name)

        return missing_slots

    def _save_context_to_history(self, user_id: str, context: Dict[str, Any]) -> None:
        """
        保存上下文到历史记录

        Args:
            user_id: 用户ID
            context: 当前上下文
        """
        try:
            cache_key = f"context_history:{user_id}"
            # 添加时间戳用于过期检查
            context['timestamp'] = datetime.now().timestamp()
            self.cache.set(cache_key, context, expire=self.cache_expire_time)
        except Exception as e:
            logger.warning(f"保存上下文历史失败: {e}")

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
