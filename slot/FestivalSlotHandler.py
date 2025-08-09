# E:\work\waiter\slot\FestivalSlotHandler.py
"""
节日槽位处理器
"""

from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.features_dict import festival_dates
import re
from datetime import datetime


class FestivalSlotHandler(SlotHandler):
    """节日槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从festival_dates中获取节日词典
        self.festival_keywords = list(festival_dates.keys())
        # 按长度排序，优先匹配长词汇
        self.festival_keywords.sort(key=len, reverse=True)
        # 保存节日数据用于后续处理
        self.festival_data = festival_dates

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)

        # 获取当前日期
        current_date = datetime.now()

        if text_to_process:
            # 提取节日信息
            festival_info = self._extract_festival_info(text_to_process)
        else:
            # 如果没有文本输入，检查是否临近节日
            festival_info = self._get_upcoming_festival(current_date)

        # 将节日信息添加到slots中
        slots = context.setdefault('slots', {})

        # 如果提取到节日信息，则更新slots
        if festival_info:
            slots['节日'] = festival_info
            # 添加节日的详细信息
            if festival_info in self.festival_data:
                slots['节日信息'] = self.festival_data[festival_info]

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

    def _extract_festival_info(self, text: str) -> Optional[str]:
        """
        从文本中提取节日信息

        Args:
            text: 输入文本

        Returns:
            识别到的节日，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的节日
        for festival in self.festival_keywords:
            # 将节日名称也转为小写进行匹配
            festival_lower = festival.lower()

            # 精确匹配整个词
            if festival_lower in processed_text:
                return festival  # 返回原始大小写的节日名称

        return None

    def _get_upcoming_festival(self, current_date: datetime) -> Optional[str]:
        """
        根据当前日期获取临近的节日

        Args:
            current_date: 当前日期

        Returns:
            临近的节日名称，如果没有则返回None
        """
        # 获取当前年份
        current_year = current_date.year

        # 检查固定日期节日（阳历）
        for festival, info in self.festival_data.items():
            solar_date = info.get("阳历")
            if solar_date:
                try:
                    # 解析日期格式 "月日" 如 "2月14日"
                    if "月" in solar_date and "日" in solar_date:
                        month_day = solar_date.replace("月", "-").replace("日", "")
                        month, day = map(int, month_day.split("-"))

                        # 创建今年和明年的节日日期
                        festival_this_year = datetime(current_year, month, day)
                        festival_next_year = datetime(current_year + 1, month, day)

                        # 检查是否在接下来30天内
                        days_until_this_year = (festival_this_year - current_date).days
                        days_until_next_year = (festival_next_year - current_date).days

                        if 0 <= days_until_this_year <= 30:
                            return festival
                        elif 0 <= days_until_next_year <= 30:
                            return festival
                except Exception:
                    continue

        # 特殊处理一些常见节日
        # 检查是否接近周末（可能关联到一些非正式节日）
        weekday = current_date.weekday()
        # 如果是周五，可能是"周末"
        if weekday == 4:  # 周五
            return "周末"
        # 如果是周六或周日，也可能是"周末"
        elif weekday in [5, 6]:  # 周六或周日
            return "周末"

        return None


# 测试代码
def test_festival_slot_handler():
    """测试节日槽位处理器"""
    print("=" * 50)
    print("测试节日槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = FestivalSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "识别情人节",
            "context": {
                "cleaned_text": "情人节想和女朋友一起过"
            }
        },
        {
            "name": "识别春节",
            "context": {
                "cleaned_text": "春节回家团圆饭"
            }
        },
        {
            "name": "识别圣诞节",
            "context": {
                "cleaned_text": "圣诞节平安夜一起吃大餐"
            }
        },
        {
            "name": "识别母亲节",
            "context": {
                "cleaned_text": "母亲节给妈妈准备惊喜"
            }
        },
        {
            "name": "无节日描述",
            "context": {
                "cleaned_text": "我想吃火锅"
            }
        },
        {
            "name": "多种节日选择第一个",
            "context": {
                "cleaned_text": "情人节和圣诞节都想要浪漫晚餐"
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
            print(f"提取的节日: {slots.get('节日', '未提取到')}")
            if '节日信息' in slots:
                print(f"节日信息: {slots['节日信息']}")

        except Exception as e:
            print(f"处理出错: {e}")

    # 测试无输入文本情况（检查临近节日）
    print(f"\n测试临近节日检测:")
    try:
        context = {}
        result_context = handler.handle(context)
        slots = result_context.get('slots', {})
        print(f"临近节日: {slots.get('节日', '未检测到临近节日')}")
    except Exception as e:
        print(f"处理出错: {e}")


if __name__ == "__main__":
    test_festival_slot_handler()
