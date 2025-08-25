# E:\work\waiter\slot\SinglePersonSceneHandler.py
"""
一个人用餐场景处理器
"""

from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import re
import logging

logger = logging.getLogger(__name__)

class SinglePersonSceneHandler(SlotHandler):
    """一个人用餐场景处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 定义匹配一个人用餐的关键词和模式
        self.single_patterns = [
            r'一个人',
            r'独自',
            r'单人',
            r'我一个人',
            r'就我一个',
            r'只有我',
            r'solo',
            r'独自用餐',
            r'一个人吃饭'
        ]

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)
            
            if text_to_process:
                # 检查是否匹配一个人用餐的场景
                if self._is_single_person_scene(text_to_process):
                    # 设置场景为"独自用餐"
                    slots = context.setdefault('slots', {})
                    slots['场景'] = '独自用餐'
                    # 设置人数为1
                    slots['人数'] = 1
                    logger.info("识别到一个人用餐场景")

        except Exception as e:
            logger.error(f"一个人用餐场景处理出错: {e}")

        return super().handle(context)

    def _get_text_to_process(self, context: Dict[str, Any]) -> str:
        """按优先级获取处理文本"""
        text_sources = [
            context.get('cleaned_text'),
            context.get('input_text'),
            context.get('tokenized_text')
        ]
        
        for text in text_sources:
            if text:
                return text
        return ""

    def _is_single_person_scene(self, text: str) -> bool:
        """判断是否为一个人用餐场景"""
        processed_text = text.lower().strip()
        
        # 检查是否匹配任何一个人用餐的模式
        for pattern in self.single_patterns:
            if re.search(pattern, processed_text):
                return True
                
        return False
