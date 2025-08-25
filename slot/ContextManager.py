# ContextManager.py (更新版)
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from slot.SlotManager import SlotManager

logger = logging.getLogger(__name__)

class ContextManager:
    """统一的Context管理器"""

    def __init__(self):
        self.context = self._create_default_context()
        self.slot_manager = SlotManager()

    def _create_default_context(self) -> Dict[str, Any]:
        """创建默认的Context结构"""
        return {
            'input': {
                'text': '',
                'cleaned_text': '',
                'tokenized_text': ''
            },
            'user': {
                'id': None,
                'session_id': None,
                'ip': None
            },
            'recognition': {
                'intent': 'default',
                'slots': {},
                'is_order': False
            },
            'environment': {
                'location': '北京',
                'location_info': {},
                'weather_info': {"天气": "未知"}
            },
            'history': {
                'input_text':[],
                'orders': [],
                'games': []
            },
            'processing': {
                'missing_slots': [],
                'need_user_input': False,
                'prompt_message': ''
            },
            'output': {
                'context_dict': {},
                'template_name': 'enhanced_basic_with_all',
                'language': 'zh-CN',
                'result': ''
            },
            'errors': []
        }

    def update_context(self, updates: Dict[str, Any]) -> None:
        """安全地更新Context"""
        def deep_update(d, u):
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    deep_update(d[k], v)
                else:
                    d[k] = v
            return d

        deep_update(self.context, updates)

    def get_context(self) -> Dict[str, Any]:
        """获取当前Context"""
        return self.context.copy()

    def set_slot(self, slot_name: str, slot_value: Any) -> bool:
        """统一设置槽位，包含验证"""
    # 验证槽位值
        if not self.slot_manager.validate_slot(slot_name, slot_value):
            logger.warning(f"槽位值验证失败: {slot_name} = {slot_value}")
            return False

        if 'recognition' not in self.context:
            self.context['recognition'] = {}
        if 'slots' not in self.context['recognition']:
            self.context['recognition']['slots'] = {}

        self.context['recognition']['slots'][slot_name] = slot_value

        # 同步更新相关字段
        if slot_name == '城市':
            self.context['environment']['location'] = slot_value

        logger.info(f"设置槽位: {slot_name} = {slot_value}")
        return True

    def get_slot(self, slot_name: str, default=None) -> Any:
        """统一获取槽位"""
        return self.context.get('recognition', {}).get('slots', {}).get(slot_name, default)

    def add_error(self, processor_name: str, error: Exception) -> None:
        """添加错误信息"""
        self.context.setdefault('errors', []).append({
            'processor': processor_name,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        logger.error(f"Processor {processor_name} failed: {error}")

# 全局Context管理器实例
_context_manager = None

def get_context_manager() -> ContextManager:
    """获取全局Context管理器实例"""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager
