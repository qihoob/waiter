# E:\work\waiter\slot\PeopleCountSlotHandler.py
"""
人数槽位处理器
"""

from typing import Dict, Any, Optional
from slot.SlotHandler import SlotHandler
import re


class PeopleCountSlotHandler(SlotHandler):
    """人数槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        self.chinese_to_num = {
            '一': 1,
            '二': 2,
            '两': 2,
            '三': 3,
            '四': 4,
            '五': 5,
            '六': 6,
            '七': 7,
            '八': 8,
            '九': 9,
            '十': 10
        }

        # 表示人的关键词
        self.people_keywords = ['人', '位', '客']

        # 表示份数的关键词
        self.portion_keywords = ['份', '餐', '杯', '盘', '碗']

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)

        if text_to_process:
            # 提取人数信息
            people_count = self._extract_people_count(text_to_process)

            # 将人数信息添加到slots中
            slots = context.setdefault('slots', {})

            # 如果提取到人数信息，则更新slots
            if people_count is not None:
                slots['人数'] = people_count

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

    def _extract_people_count(self, text: str) -> Optional[int]:
        """
        从文本中提取人数信息

        Args:
            text: 输入文本

        Returns:
            识别到的人数，如果没有则返回None
        """
        # 1. 先尝试匹配阿拉伯数字 + 关键词的情况
        pattern = r'(\d+)([人位客])'
        match = re.search(pattern, text)
        if match:
            count = int(match.group(1))
            if self._is_valid_count(count):
                return count

        # 2. 再尝试匹配中文数字 + 关键词的情况
        for keyword in self.people_keywords:
            for chinese_num, num in self.chinese_to_num.items():
                if chinese_num + keyword in text:
                    return num

        # 3. 特殊情况："一个人吃饭" 这种结构
        pattern = r'([一二两三四五六七八九十]|[\d]+)个(人)'
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1)
            if num_str.isdigit():
                count = int(num_str)
            else:
                count = self.chinese_to_num.get(num_str)

            if count is not None and self._is_valid_count(count):
                return count

        # 4. 匹配"份"的情况，如"1份牛排"
        for keyword in self.portion_keywords:
            pattern = rf'(\d+)个?{keyword}'
            match = re.search(pattern, text)
            if match:
                count = int(match.group(1))
                # 对于"份"的情况，我们假设通常不会超过20份
                if self._is_valid_count(count):
                    return count

        return None

    def _is_valid_count(self, count: int) -> bool:
        """
        验证数量是否在合理范围内

        Args:
            count: 数量

        Returns:
            是否为有效数量
        """
        # 人数应该在1-50之间，这是一个合理的范围
        return 1 <= count <= 50


# 测试代码
def test_people_count_slot_handler():
    """测试人数槽位处理器"""
    print("=" * 50)
    print("测试人数槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = PeopleCountSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "阿拉伯数字+人",
            "context": {
                "cleaned_text": "我们3个人一起吃饭"
            }
        },
        {
            "name": "中文数字+位",
            "context": {
                "cleaned_text": "订4位客人的位置"
            }
        },
        {
            "name": "中文数字+人",
            "context": {
                "cleaned_text": "一个人吃饭"
            }
        },
        {
            "name": "份数表达",
            "context": {
                "cleaned_text": "我要2份牛排"
            }
        },
        {
            "name": "无数量描述",
            "context": {
                "cleaned_text": "我想吃火锅"
            }
        },
        {
            "name": "无效数量",
            "context": {
                "cleaned_text": "100个人一起聚餐"
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
            people_count = slots.get('人数', '未提取到')
            print(f"提取的人数: {people_count}")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_people_count_slot_handler()
