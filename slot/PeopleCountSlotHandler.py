# PeopleCountSlotHandler.py (优化版)
from typing import Dict, Any, Optional
from slot.BaseSlotHandler import BaseSlotHandler
import re
import logging

logger = logging.getLogger(__name__)

class PeopleCountSlotHandler(BaseSlotHandler):
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
        try:
            text_to_process = self._get_text_to_process(context)
            if text_to_process:
                people_count = self._extract_people_count(text_to_process)
                if people_count is not None:
                    self._set_slot(context, '人数', people_count)
                    logger.info(f"提取到人数: {people_count}")
        except Exception as e:
            logger.error(f"人数槽位处理出错: {e}")

        return super().handle(context)

    def _extract_people_count(self, text: str) -> Optional[int]:
        """
        从文本中提取人数
        
        Args:
            text: 输入文本
            
        Returns:
            提取到的人数，如果没有则返回None
        """
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
        pattern = r'(\d+)个?[份餐]'
        match = re.search(pattern, text)
        if match:
            count = int(match.group(1))
            # 对于"份"的情况，我们假设通常不会超过20份
            if 1 <= count <= 20:
                return count

        # 基于人称代词推断人数
        for pattern, default in self.pronoun_patterns:
            if re.search(pattern, text):
                return default

        # 基于场景关键词推断人数
        for pattern, default in self.implicit_people_patterns:
            if re.search(pattern, text):
                return default

        return None
