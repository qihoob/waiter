# E:\work\waiter\slot\HealthPreferenceSlotHandler.py
"""
健康偏好槽位处理器
"""

from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.config import SLOT_DICT
import re


class HealthPreferenceSlotHandler(SlotHandler):
    """健康偏好槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取健康偏好词典
        self.health_preference_keywords = SLOT_DICT.get("健康偏好", [])
        # 按长度排序，优先匹配长词汇
        self.health_preference_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)

        if text_to_process:
            # 提取健康偏好信息
            health_preference_info = self._extract_health_preference_info(text_to_process)

            # 将健康偏好信息添加到slots中
            slots = context.setdefault('slots', {})

            # 如果提取到健康偏好信息，则更新slots
            if health_preference_info:
                slots['健康偏好'] = health_preference_info

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

    def _extract_health_preference_info(self, text: str) -> Optional[str]:
        """
        从文本中提取健康偏好信息

        Args:
            text: 输入文本

        Returns:
            识别到的健康偏好，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的健康偏好
        for preference in self.health_preference_keywords:
            # 将健康偏好词也转为小写进行匹配
            preference_lower = preference.lower()

            # 精确匹配整个词
            if preference_lower in processed_text:
                return preference  # 返回原始大小写的健康偏好词

        return None


# 测试代码
def test_health_preference_slot_handler():
    """测试健康偏好槽位处理器"""
    print("=" * 50)
    print("测试健康偏好槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = HealthPreferenceSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "识别低脂偏好",
            "context": {
                "cleaned_text": "我要低脂的食物，不能太油腻"
            }
        },
        {
            "name": "识别清淡口味",
            "context": {
                "cleaned_text": "最近想吃清淡一点的，少油少盐"
            }
        },
        {
            "name": "识别减肥餐",
            "context": {
                "cleaned_text": "我在减肥，想要减肥餐"
            }
        },
        {
            "name": "识别素食偏好",
            "context": {
                "cleaned_text": "我是素食主义者，不要肉"
            }
        },
        {
            "name": "无健康偏好描述",
            "context": {
                "cleaned_text": "我想吃火锅"
            }
        },
        {
            "name": "多种健康偏好选择第一个",
            "context": {
                "cleaned_text": "要低脂又高蛋白的食物"
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
            print(f"提取的健康偏好: {slots.get('健康偏好', '未提取到')}")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_health_preference_slot_handler()
