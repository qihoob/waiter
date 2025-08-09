# E:\work\waiter\slot\DietaryRestrictionSlotHandler.py
"""
忌口槽位处理器
"""

from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.config import SLOT_DICT
import re


class DietaryRestrictionSlotHandler(SlotHandler):
    """忌口槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取忌口词典
        self.dietary_restriction_keywords = SLOT_DICT.get("忌口", [])
        # 按长度排序，优先匹配长词汇
        self.dietary_restriction_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)

        if text_to_process:
            # 提取所有忌口信息
            dietary_restriction_info_list = self._extract_all_dietary_restriction_info(text_to_process)

            # 将忌口信息添加到slots中
            slots = context.setdefault('slots', {})

            # 如果提取到忌口信息，则更新slots
            if dietary_restriction_info_list:
                # 忌口以列表形式存储
                if '忌口' not in slots:
                    slots['忌口'] = []

                # 确保slots['忌口']是列表类型
                if not isinstance(slots['忌口'], list):
                    slots['忌口'] = [slots['忌口']]

                # 添加所有找到的忌口，避免重复
                for restriction in dietary_restriction_info_list:
                    if restriction not in slots['忌口']:
                        slots['忌口'].append(restriction)

        return super().handle(context)

    def _get_text_to_process(self, context: Dict[str, Any]) -> Optional[str]:
        """
        获取需要处理的文本

        Args:
            context: 处理上下文

        Returns:
            需要处理的文本，如果没有则返回None
        """
        # 按优先级获取文本
        text_sources = [
            context.get('cleaned_text'),
            context.get('input_text'),
            context.get('tokenized_text')
        ]

        for text in text_sources:
            if text:
                return text

        return None

    def _extract_all_dietary_restriction_info(self, text: str) -> List[str]:
        """
        从文本中提取所有忌口信息

        Args:
            text: 输入文本

        Returns:
            识别到的忌口信息列表
        """
        found_restrictions = []
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的忌口信息
        for restriction in self.dietary_restriction_keywords:
            # 将忌口词也转为小写进行匹配
            restriction_lower = restriction.lower()

            # 精确匹配整个词
            if restriction_lower in processed_text and restriction not in found_restrictions:
                found_restrictions.append(restriction)  # 返回原始大小写的忌口词

        return found_restrictions


# 测试代码
def test_dietary_restriction_slot_handler():
    """测试忌口槽位处理器"""
    print("=" * 50)
    print("测试忌口槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = DietaryRestrictionSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "识别不吃辣",
            "context": {
                "cleaned_text": "我不能吃辣的，太辣了受不了"
            }
        },
        {
            "name": "识别忌海鲜",
            "context": {
                "cleaned_text": "我对海鲜过敏，不能吃海鲜"
            }
        },
        {
            "name": "识别忌生冷",
            "context": {
                "cleaned_text": "不要生冷的食物，要热乎的"
            }
        },
        {
            "name": "识别忌油腻",
            "context": {
                "cleaned_text": "最近想吃清淡的，不要太油腻"
            }
        },
        {
            "name": "无忌口描述",
            "context": {
                "cleaned_text": "我想吃火锅"
            }
        },
        {
            "name": "多种忌口",
            "context": {
                "cleaned_text": "不吃辣也不吃海鲜"
            }
        },
        {
            "name": "三种忌口",
            "context": {
                "cleaned_text": "不吃辣、不吃海鲜，也不要太油腻"
            }
        }
    ]

    # 执行测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"输入文本: {test_case['context']['cleaned_text']}")

        try:
            # 执行处理
            result_context = handler.handle(test_case['context'].copy())

            # 输出结果
            slots = result_context.get('slots', {})
            restrictions = slots.get('忌口', '未提取到')
            print(f"提取的忌口: {restrictions}")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_dietary_restriction_slot_handler()
