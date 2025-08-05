from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class SlotHandler(ABC):
    """槽位处理责任链的抽象基类"""

    def __init__(self, next_handler: Optional['SlotHandler'] = None):
        self._next_handler = next_handler

    def set_next(self, handler: 'SlotHandler') -> 'SlotHandler':
        """设置下一个处理器"""
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理槽位"""
        if self._next_handler:
            return self._next_handler.handle(context)
        return context