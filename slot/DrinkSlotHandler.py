# E:\work\waiter\slot\DrinkSlotHandler.py
"""
饮品槽位处理器
"""

from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.config import SLOT_DICT
import re


class DrinkSlotHandler(SlotHandler):
    """饮品槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取饮品词典
        self.drink_keywords = SLOT_DICT.get("饮品", [])
        # 按长度排序，优先匹配长词汇
        self.drink_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)

        if text_to_process:
            # 提取饮品信息
            drink_info = self._extract_drink_info(text_to_process)

            # 将饮品信息添加到slots中
            slots = context.setdefault('slots', {})

            # 如果提取到饮品信息，则更新slots
            if drink_info:
                slots['饮品'] = drink_info

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

    def _extract_drink_info(self, text: str) -> Optional[str]:
        """
        从文本中提取饮品信息

        Args:
            text: 输入文本

        Returns:
            识别到的饮品名称，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的饮品
        for drink in self.drink_keywords:
            # 将饮品名称也转为小写进行匹配
            drink_lower = drink.lower()

            # 精确匹配整个词
            if drink_lower in processed_text:
                return drink  # 返回原始大小写的饮品名称

        return None


# 测试代码
def test_drink_slot_handler():
    """测试饮品槽位处理器"""
    print("=" * 50)
    print("测试饮品槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = DrinkSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "识别具体饮品",
            "context": {
                "cleaned_text": "我想要一杯可口可乐"
            }
        },
        {
            "name": "识别茶类饮品",
            "context": {
                "cleaned_text": "来杯珍珠奶茶和冰红茶"
            }
        },
        {
            "name": "识别酒精饮品",
            "context": {
                "cleaned_text": "晚上想喝啤酒，最好是精酿"
            }
        },
        {
            "name": "识别咖啡类",
            "context": {
                "cleaned_text": "早上来杯美式咖啡提神"
            }
        },
        {
            "name": "无饮品文本",
            "context": {
                "cleaned_text": "我想吃汉堡和薯条"
            }
        },
        {
            "name": "多种饮品选择第一个",
            "context": {
                "cleaned_text": "要可口可乐还是百事可乐"
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
            print(f"提取的饮品: {slots.get('饮品', '未提取到')}")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_drink_slot_handler()
