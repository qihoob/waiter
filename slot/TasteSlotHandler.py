# E:\work\waiter\slot\TasteSlotHandler.py
"""
口味槽位处理器
"""

from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.config import SLOT_DICT
import re


class TasteSlotHandler(SlotHandler):
    """口味槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取口味词典
        self.taste_keywords = SLOT_DICT.get("口味", [])
        # 按长度排序，优先匹配长词汇
        self.taste_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)

        if text_to_process:
            # 提取口味信息
            taste_info = self._extract_taste_info(text_to_process)

            # 将口味信息添加到slots中
            slots = context.setdefault('slots', {})

            # 如果提取到口味信息，则更新slots
            if taste_info:
                slots['口味'] = taste_info

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

    def _extract_taste_info(self, text: str) -> Optional[str]:
        """
        从文本中提取口味信息

        Args:
            text: 输入文本

        Returns:
            识别到的口味，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的口味
        for taste in self.taste_keywords:
            # 将口味词也转为小写进行匹配
            taste_lower = taste.lower()

            # 精确匹配整个词
            if taste_lower in processed_text:
                return taste  # 返回原始大小写的口味词

        return None


# 测试代码
def test_taste_slot_handler():
    """测试口味槽位处理器"""
    print("=" * 50)
    print("测试口味槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = TasteSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "识别辣味",
            "context": {
                "cleaned_text": "我想要麻辣口味的火锅"
            }
        },
        {
            "name": "识别甜味",
            "context": {
                "cleaned_text": "来点甜酸口味的糖醋里脊"
            }
        },
        {
            "name": "识别清淡口味",
            "context": {
                "cleaned_text": "最近想吃清淡一点的食物"
            }
        },
        {
            "name": "识别香味",
            "context": {
                "cleaned_text": "这道菜蒜香味很浓"
            }
        },
        {
            "name": "无口味描述",
            "context": {
                "cleaned_text": "我想吃米饭和蔬菜"
            }
        },
        {
            "name": "多种口味选择第一个",
            "context": {
                "cleaned_text": "要微辣的酸甜口味"
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
            print(f"提取的口味: {slots.get('口味', '未提取到')}")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_taste_slot_handler()
