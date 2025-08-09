from typing import Dict, Any, Optional
from slot.SlotHandler import SlotHandler
import re


class PeopleCountSlotHandler(SlotHandler):
    """人数槽位处理器（优化版）"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        self.chinese_to_num = {
            '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
        }

        # 表示人的关键词
        self.people_keywords = ['人', '位', '客']

        # 表示份数的关键词
        self.portion_keywords = ['份', '餐', '杯', '盘', '碗']

        # 人称代词与默认人数映射（优先级：具体表述 > 人称代词）
        self.pronoun_patterns = [
            (r'^我(?!们).*', 1),               # 单独"我"默认1人（排除"我们"）
            (r'我们|咱(们)?', 2),               # "我们/咱们"默认2人
            (r'我和(?:他|她|朋友|同事|家人)', 2),  # "我和X"默认2人
            (r'我和(?:他们|她们|朋友们|同事们)', 3)  # "我和XX们"默认3人
        ]

        # 隐含人数的场景关键词
        self.implicit_people_patterns = [
            (r'聚餐|聚会', 3),      # 聚餐/聚会默认3人及以上
            (r'大家|一群人', 4),    # 大家/一群人默认4人及以上
            (r'家庭(?:聚餐|吃饭)', 4),  # 家庭场景默认4人及以上
            (r'团队|部门', 5)       # 团队/部门默认5人及以上
        ]

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self._get_text_to_process(context)
        return super().handle(context)

    def _get_text_to_process(self, context: Dict[str, Any]) -> Optional[str]:
        """按优先级获取处理文本"""
        text_sources = [
            context.get('cleaned_text'),
            context.get('input_text'),
            context.get('tokenized_text')
        ]
        for text in text_sources:
            if text:
                people_count = self._extract_people_count(text)
                if people_count is not None:
                    context.setdefault('slots', {})['人数'] = people_count
        return None

    def _extract_people_count(self, text: str) -> Optional[int]:
        """提取人数（新增人称代词识别逻辑）"""
        # 1. 优先匹配明确数字+关键词（最高优先级）
        explicit_count = self._extract_explicit_count(text)
        if explicit_count is not None:
            return explicit_count

        # 2. 处理人称代词推断（次高优先级）
        pronoun_count = self._extract_pronoun_based_count(text)
        if pronoun_count is not None:
            return pronoun_count

        # 3. 处理隐含场景推断（低优先级）
        implicit_count = self._extract_implicit_count(text)
        if implicit_count is not None:
            return implicit_count

        return None

    def _extract_explicit_count(self, text: str) -> Optional[int]:
        """提取明确数字+关键词的情况（如3人、两位）"""
        # 阿拉伯数字+人/位/客
        match = re.search(r'(\d+)([人位客])', text)
        if match:
            count = int(match.group(1))
            if self._is_valid_count(count):
                return count

        # 中文数字+人/位/客
        for keyword in self.people_keywords:
            for cn_num, num in self.chinese_to_num.items():
                if f"{cn_num}{keyword}" in text:
                    return num

        # "X个+人"结构（如一个人、两个人）
        match = re.search(r'([一二两三四五六七八九十\d]+)个(人)', text)
        if match:
            num_str = match.group(1)
            count = int(num_str) if num_str.isdigit() else self.chinese_to_num.get(num_str)
            if count and self._is_valid_count(count):
                return count

        # 份数推断（如2份餐默认2人）
        for keyword in self.portion_keywords:
            match = re.search(rf'(\d+)个?{keyword}', text)
            if match:
                count = int(match.group(1))
                if self._is_valid_count(count):
                    return count

        return None

    def _extract_pronoun_based_count(self, text: str) -> Optional[int]:
        """基于人称代词推断人数（新增核心逻辑）"""
        for pattern, default in self.pronoun_patterns:
            if re.search(pattern, text):
                return default
        return None

    def _extract_implicit_count(self, text: str) -> Optional[int]:
        """基于场景关键词推断人数"""
        for pattern, default in self.implicit_people_patterns:
            if re.search(pattern, text):
                return default
        return None

    def _is_valid_count(self, count: int) -> bool:
        """验证人数合理性（1-50人）"""
        return 1 <= count <= 50


# 测试代码
def test_people_count_slot_handler():
    print("=" * 50)
    print("测试人数槽位处理器（新增人称代词识别）")
    print("=" * 50)

    handler = PeopleCountSlotHandler()
    test_cases = [
        # 明确数字场景
        {"name": "阿拉伯数字+人", "text": "我们3个人一起吃饭", "expected": 3},
        {"name": "中文数字+位", "text": "订两位客人的位置", "expected": 2},
        {"name": "X个+人", "text": "一个人吃饭", "expected": 1},
        {"name": "份数推断", "text": "我要4份牛排", "expected": 4},

        # 人称代词场景（新增测试）
        {"name": "单独我", "text": "我想订个位置", "expected": 1},
        {"name": "我们", "text": "我们去吃火锅", "expected": 2},
        {"name": "我和朋友", "text": "我和朋友约饭", "expected": 2},
        {"name": "我和同事们", "text": "我和同事们聚餐", "expected": 3},
        {"name": "咱们", "text": "咱们明天一起吃饭", "expected": 2},

        # 隐含场景
        {"name": "聚餐", "text": "晚上聚餐", "expected": 3},
        {"name": "家庭聚餐", "text": "家庭聚餐安排一下", "expected": 4},
        {"name": "团队", "text": "部门团队吃饭", "expected": 5},

        # 无明确信息
        {"name": "无人数信息", "text": "我想吃火锅", "expected": 1},  # 触发"我"的默认
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {case['name']}")
        print(f"输入文本: {case['text']}")
        context = handler.handle({"cleaned_text": case["text"]})
        result = context.get('slots', {}).get('人数', '未提取到')
        print(f"提取结果: {result} (预期: {case['expected']})")


if __name__ == "__main__":
    test_people_count_slot_handler()