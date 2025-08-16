# SlotManager.py
"""
槽位管理器，统一管理所有槽位的处理和验证
"""

from typing import Dict, Any, List, Set
from slot.slot_definitions import SLOT_DEFINITIONS, INTENT_REQUIRED_SLOTS
import logging

logger = logging.getLogger(__name__)

class SlotManager:
    """槽位管理器"""

    def __init__(self):
        self.slot_definitions = SLOT_DEFINITIONS
        self.intent_required_slots = INTENT_REQUIRED_SLOTS

    def validate_slot(self, slot_name: str, slot_value: Any) -> bool:
        """
        验证槽位值是否有效

        Args:
            slot_name: 槽位名称
            slot_value: 槽位值

        Returns:
            bool: 是否有效
        """
        if slot_name not in self.slot_definitions:
            logger.warning(f"未知槽位: {slot_name}")
            return False

        slot_def = self.slot_definitions[slot_name]
        slot_type = slot_def["type"]

        # 根据槽位类型进行验证
        if slot_type == "numeric":
            try:
                float(slot_value)
                return True
            except (ValueError, TypeError):
                return False
        elif slot_type == "list":
            return isinstance(slot_value, (list, tuple))
        elif slot_type == "dict":
            return isinstance(slot_value, dict)
        else:
            # categorical, location, text类型
            return isinstance(slot_value, str) and len(slot_value.strip()) > 0

    def get_required_slots_for_intent(self, intent: str) -> Set[str]:
        """
        根据意图获取需要的槽位集合

        Args:
            intent: 用户意图

        Returns:
            Set[str]: 需要的槽位集合
        """
        # 精确匹配意图
        if intent in self.intent_required_slots:
            return self.intent_required_slots[intent].copy()

        # 模糊匹配意图（前缀匹配）
        for intent_prefix, slots in self.intent_required_slots.items():
            if intent.startswith(intent_prefix):
                return slots.copy()

        # 返回默认槽位
        return self.intent_required_slots.get("default", set()).copy()

    def validate_required_slots(self, slots: Dict[str, Any], required_slots: Set[str]) -> List[str]:
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
            # 检查槽位是否存在且不为空且有效
            if (slot_name not in slots or
                not slots[slot_name] or
                not self.validate_slot(slot_name, slots[slot_name])):
                missing_slots.append(slot_name)

        return missing_slots

    def merge_slots(self, existing_slots: Dict[str, Any], new_slots: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并槽位信息，新槽位优先级更高

        Args:
            existing_slots: 现有槽位
            new_slots: 新槽位

        Returns:
            Dict[str, Any]: 合并后的槽位
        """
        merged_slots = existing_slots.copy()
        merged_slots.update(new_slots)
        return merged_slots

    def get_slot_description(self, slot_name: str) -> Dict[str, Any]:
        """
        获取槽位描述信息

        Args:
            slot_name: 槽位名称

        Returns:
            Dict[str, Any]: 槽位描述信息
        """
        return self.slot_definitions.get(slot_name, {})
