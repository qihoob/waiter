# SlotUtils.py
"""
槽位处理工具类
"""

from typing import Dict, Any, List, Set
from slot.SlotManager import SlotManager
import logging

logger = logging.getLogger(__name__)

class SlotUtils:
    """槽位处理工具类"""

    @staticmethod
    def format_slot_value(slot_name: str, slot_value: Any) -> Any:
        """
        格式化槽位值

        Args:
            slot_name: 槽位名称
            slot_value: 槽位值

        Returns:
            Any: 格式化后的槽位值
        """
        # 移除常见的单位后缀
        if isinstance(slot_value, str):
            # 对于人数槽位，提取数字部分
            if slot_name == "人数":
                import re
                match = re.search(r'(\d+)', slot_value)
                if match:
                    return int(match.group(1))

            # 对于预算槽位，提取数字部分
            if slot_name == "预算":
                import re
                match = re.search(r'(\d+)', slot_value)
                if match:
                    return int(match.group(1))

        return slot_value

    @staticmethod
    def normalize_slot_name(slot_name: str) -> str:
        """
        标准化槽位名称

        Args:
            slot_name: 原始槽位名称

        Returns:
            str: 标准化后的槽位名称
        """
        # 统一槽位名称
        name_mapping = {
            "城市": "城市",
            "city": "城市",
            "地区": "地区",
            "region": "地区",
            "天气状态": "天气",
            "weather": "天气"
        }

        return name_mapping.get(slot_name, slot_name)

    @staticmethod
    def get_slot_prompt(slot_name: str) -> str:
        """
        获取槽位提示信息

        Args:
            slot_name: 槽位名称

        Returns:
            str: 提示信息
        """
        prompts = {
            "场景": "请问您是在什么场景下用餐？(例如: 朋友聚会、家庭聚餐、商务宴请等)",
            "人数": "请问有多少人用餐？",
            "菜系": "您想吃什么菜系？(例如: 川菜、粤菜、日料等)",
            "口味": "您偏好什么口味？(例如: 辣味、清淡、酸甜等)",
            "健康偏好": "您有什么健康偏好？(例如: 低脂、高蛋白、无糖等)",
            "忌口": "您有什么忌口的食物吗？",
            "过敏原": "您对什么食物过敏？",
            "游戏": "您想玩什么游戏？",
            "饮品": "您想喝什么饮品？",
            "节日": "您想了解哪个节日的活动？"
        }

        return prompts.get(slot_name, f"请提供{slot_name}信息")

# 导出实例
slot_manager = SlotManager()
slot_utils = SlotUtils()
