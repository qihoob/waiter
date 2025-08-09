# E:\work\waiter\slot\PeopleCountSlotHandler.py
from typing import Dict, Any
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

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        slots = context.get('slots', {})
        people_count = slots.get('人数')
        # 处理人数相关的逻辑
        if people_count is None:
            # 检查 input_text 是否存在再尝试提取
            if 'input_text' in context:
                people_count = self.extract_people_count(context['input_text'])
        if people_count is None:
            # 检查 cleaned_text 是否存在再尝试提取
            if 'cleaned_text' in context:
                people_count = self.extract_people_count(context['cleaned_text'])
        if people_count is not None:
            slots['人数'] = people_count
        return super().handle(context)

    def extract_people_count(self, text):
        # 先尝试匹配阿拉伯数字 + 关键词的情况
        pattern = r'(\d+)([人位客])'
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

        # 再尝试匹配中文数字 + 关键词的情况
        for keyword in self.people_keywords:
            for chinese_num, num in self.chinese_to_num.items():
                if chinese_num + keyword in text:
                    return num

        # 特殊情况："一个人吃饭" 这种结构
        pattern = r'([一二两三四五六七八九十]|[\d]+)个(人)'
        match = re.search(pattern, text)
        if match:
            num_str = match.group(1)
            if num_str.isdigit():
                return int(num_str)
            return self.chinese_to_num.get(num_str, None)

        # 匹配"份"的情况，如"1份牛排"
        pattern = r'(\d+)个?[份餐杯]'
        match = re.search(pattern, text)
        if match:
            count = int(match.group(1))
            # 对于"份"的情况，我们假设通常不会超过20份
            if 1 <= count <= 20:
                return count

        return None
