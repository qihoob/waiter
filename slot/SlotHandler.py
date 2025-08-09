# E:\work\waiter\slot\SlotHandler.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

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

class SlotHandlerInterrupt(Exception):
    """槽位处理器中断异常，用于中断责任链执行"""

    def __init__(self, result: Dict[str, Any]):
        self.result = result
        super().__init__("Slot processing chain interrupted")
