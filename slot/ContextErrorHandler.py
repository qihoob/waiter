# error_handler.py
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextErrorHandler:
    """Context错误处理机制"""
    
    @staticmethod
    def handle_processor_error(context: Dict[str, Any], processor_name: str, error: Exception) -> Dict[str, Any]:
        """处理处理器错误"""
        # 记录错误日志
        logger.error(f"Processor {processor_name} failed: {error}")
        
        # 在context中记录错误状态
        if 'errors' not in context:
            context['errors'] = []
            
        context['errors'].append({
            'processor': processor_name,
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        })
        
        # 返回安全的context状态
        return context
        
    @staticmethod
    def has_errors(context: Dict[str, Any]) -> bool:
        """检查context中是否有错误"""
        return bool(context.get('errors'))
        
    @staticmethod
    def get_latest_error(context: Dict[str, Any]) -> Dict[str, Any]:
        """获取最新的错误信息"""
        errors = context.get('errors', [])
        return errors[-1] if errors else {}
