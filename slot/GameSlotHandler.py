# E:\work\waiter\slot\GameSlotHandler.py
"""
游戏槽位处理器
"""

from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.config import SLOT_DICT
import re


class GameSlotHandler(SlotHandler):
    """游戏槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取游戏词典
        self.game_keywords = SLOT_DICT.get("游戏", [])
        # 按长度排序，优先匹配长词汇
        self.game_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)

        if text_to_process:
            # 提取游戏信息
            game_info = self._extract_game_info(text_to_process)

            # 将游戏信息添加到slots中
            slots = context.setdefault('slots', {})

            # 如果提取到游戏信息，则更新slots
            if game_info:
                slots['游戏'] = game_info

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

    def _extract_game_info(self, text: str) -> Optional[str]:
        """
        从文本中提取游戏信息
        
        Args:
            text: 输入文本
            
        Returns:
            识别到的游戏，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()

        # 查找匹配的游戏
        for game in self.game_keywords:
            # 将游戏名称也转为小写进行匹配
            game_lower = game.lower()

            # 精确匹配整个词
            if game_lower in processed_text:
                return game  # 返回原始大小写的游戏名称

        return None


# 测试代码
def test_game_slot_handler():
    """测试游戏槽位处理器"""
    print("=" * 50)
    print("测试游戏槽位处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = GameSlotHandler()

    # 测试用例
    test_cases = [
        {
            "name": "识别桌游",
            "context": {
                "cleaned_text": "我们玩狼人杀吧"
            }
        },
        {
            "name": "识别派对游戏",
            "context": {
                "cleaned_text": "来玩真心话大冒险"
            }
        },
        {
            "name": "识别电子游戏",
            "context": {
                "cleaned_text": "一起打王者荣耀怎么样"
            }
        },
        {
            "name": "识别户外游戏",
            "context": {
                "cleaned_text": "我们去踢毽子吧"
            }
        },
        {
            "name": "无游戏描述",
            "context": {
                "cleaned_text": "我想吃火锅"
            }
        },
        {
            "name": "多种游戏选择第一个",
            "context": {
                "cleaned_text": "玩狼人杀还是斗地主"
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
            print(f"提取的游戏: {slots.get('游戏', '未提取到')}")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_game_slot_handler()
