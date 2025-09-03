# FestivalSlotHandler.py (优化版)
"""
节日槽位处理器
"""

from typing import Dict, Any, Optional
from slot.BaseSlotHandler import BaseSlotHandler
from prompt_builder.features_dict import festival_dates
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FestivalSlotHandler(BaseSlotHandler):
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
        try:
            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)

            # 获取当前日期
            current_date = datetime.now()

            festival_info = None
            if text_to_process:
                # 提取节日信息
                festival_info = self._extract_festival_info(text_to_process)
            else:
                # 如果没有文本输入，检查是否临近节日
                festival_info = self._get_upcoming_festival(current_date)

            # 如果提取到节日信息，则更新slots
            if festival_info:
                self._set_slot(context, '节日', festival_info)
                # 添加节日的详细信息
                if festival_info in self.festival_data:
                    self._set_slot(context, '节日信息', self.festival_data[festival_info])
                logger.info(f"识别到节日: {festival_info}")

        except Exception as e:
            logger.error(f"节日槽位处理出错: {e}")

        return super().handle(context)

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
                except Exception as e:
                    logger.warning(f"解析节日日期出错 {festival}: {e}")
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
