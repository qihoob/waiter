# E:\work\waiter\slot\SlotValidationHandler.py
from typing import Dict, Any, List
from slot.SlotHandler import SlotHandler
import logging

logger = logging.getLogger(__name__)

class SlotValidationHandler(SlotHandler):
    """槽位验证处理器，用于检查关键槽位是否已填写"""

    def __init__(self, required_slots: List[str] = None, next_handler=None):
        """
        初始化槽位验证处理器

        Args:
            required_slots: 必需的槽位列表
            next_handler: 下一个处理器
        """
        super().__init__(next_handler)
        # 定义关键槽位，可以根据业务需求调整
        self.required_slots = required_slots or [
            "场景",
            "人数",
            "菜系",
            "口味"
        ]

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            slots = context.get('slots', {})

            # 检查缺失的关键槽位
            missing_slots = self._validate_required_slots(slots)

            if missing_slots:
                # 如果有缺失的槽位，设置提示信息
                context['missing_slots'] = missing_slots
                context['need_user_input'] = True
                context['prompt_message'] = self._generate_prompt_message(missing_slots)

                logger.info(f"检测到缺失的关键槽位: {missing_slots}")
            else:
                # 所有关键槽位都已填写
                context['need_user_input'] = False

        except Exception as e:
            logger.error(f"槽位验证过程中出错: {e}")

        return super().handle(context)

    def _validate_required_slots(self, slots: Dict[str, Any]) -> List[str]:
        """
        验证必需的槽位是否存在

        Args:
            slots: 已提取的槽位字典

        Returns:
            List[str]: 缺失的槽位列表
        """
        missing_slots = []

        for slot_name in self.required_slots:
            # 检查槽位是否存在且不为空
            if slot_name not in slots or not slots[slot_name]:
                missing_slots.append(slot_name)

        return missing_slots

    def _generate_prompt_message(self, missing_slots: List[str]) -> str:
        """
        生成提示用户输入的消息

        Args:
            missing_slots: 缺失的槽位列表

        Returns:
            str: 提示消息
        """
        slot_prompts = {
            "场景": "请问您是在什么场景下用餐？(例如: 朋友聚会、家庭聚餐、商务宴请等)",
            "人数": "请问有多少人用餐？",
            "菜系": "您想吃什么菜系？(例如: 川菜、粤菜、日料等)",
            "口味": "您偏好什么口味？(例如: 辣味、清淡、酸甜等)"
        }

        messages = [slot_prompts.get(slot, f"请提供{slot}信息") for slot in missing_slots]
        return "为了更好地为您服务，请提供以下信息:\n" + "\n".join(messages)
