# E:\work\waiter\slot\AllergenSlotHandler.py
"""
过敏原槽位处理器
"""

from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.config import SLOT_DICT
import re


class AllergenSlotHandler(SlotHandler):
    """过敏原槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取过敏原词典
        self.allergen_keywords = SLOT_DICT.get("过敏原", [])
        # 按长度排序，优先匹配长词汇
        self.allergen_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)

        if text_to_process:
            # 提取所有过敏原信息
            allergen_info_list = self._extract_all_allergen_info(text_to_process)

            # 将过敏原信息添加到slots中
            slots = context.setdefault('slots', {})

            # 如果提取到过敏原信息，则更新slots
            if allergen_info_list:
                # 过敏原以列表形式存储
                if '过敏原' not in slots:
                    slots['过敏原'] = []

                # 确保slots['过敏原']是列表类型
                if not isinstance(slots['过敏原'], list):
                    slots['过敏原'] = [slots['过敏原']]

                # 添加所有找到的过敏原，避免重复
                for allergen in allergen_info_list:
                    if allergen not in slots['过敏原']:
                        slots['过敏原'].append(allergen)

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

    def _extract_all_allergen_info(self, text: str) -> List[str]:
        """
        从文本中提取所有过敏原信息

        Args:
            text: 输入文本

        Returns:
            识别到的过敏原信息列表
        """
        found_allergens = []
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的过敏原信息
        for allergen in self.allergen_keywords:
            # 将过敏原词也转为小写进行匹配
            allergen_lower = allergen.lower()

            # 精确匹配整个词
            if allergen_lower in processed_text and allergen not in found_allergens:
                found_allergens.append(allergen)  # 返回原始大小写的过敏原词

        return found_allergens


# 测试代码
def test_allergen_slot_handler():
    """测试过敏原槽位处理器"""
    print("=" * 50)
    print("测试过敏原槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = AllergenSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "识别花生过敏",
            "context": {
                "cleaned_text": "我对花生过敏，不能吃花生"
            }
        },
        {
            "name": "识别牛奶过敏",
            "context": {
                "cleaned_text": "我对牛奶过敏，不能喝牛奶"
            }
        },
        {
            "name": "识别海鲜过敏",
            "context": {
                "cleaned_text": "我对海鲜过敏，不能吃鱼虾"
            }
        },
        {
            "name": "识别鸡蛋过敏",
            "context": {
                "cleaned_text": "我对鸡蛋过敏，蛋糕里不要放鸡蛋"
            }
        },
        {
            "name": "无过敏原描述",
            "context": {
                "cleaned_text": "我想吃火锅"
            }
        },
        {
            "name": "多种过敏原",
            "context": {
                "cleaned_text": "对花生和牛奶都过敏"
            }
        },
        {
            "name": "三种过敏原",
            "context": {
                "cleaned_text": "我对花生、牛奶和鸡蛋都过敏"
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
            allergens = slots.get('过敏原', '未提取到')
            print(f"提取的过敏原: {allergens}")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_allergen_slot_handler()
