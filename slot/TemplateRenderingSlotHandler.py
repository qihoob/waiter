# E:\work\waiter\slot\TemplateRenderingSlotHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import logging
from slot.global_vars import get_global_template_manager
from memory.local_cache import GlobalCache
from datetime import datetime

logger = logging.getLogger(__name__)

class TemplateRenderingSlotHandler(SlotHandler):
    """模板渲染槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        self.cache = GlobalCache.get_instance()

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 渲染模板
            template_name = context.get('template_name', 'enhanced_basic_with_all')
            language = context.get('language', 'zh-CN')
            context_dict = context.get('context_dict', {})

            # 获取全局模板管理器
            template_manager = get_global_template_manager()

            rendered_prompt = template_manager.get_template(
                template_name,
                lang=language,
                **context_dict
            )

            # 清洗最终结果
            context['result'] = self._remove_empty_lines(rendered_prompt)
            logger.info("模板渲染完成")
            
            # 存储用户输入作为历史记录
            self._save_user_input_history(context)
            
        except Exception as e:
            logger.error(f"模板渲染失败: {e}")
            context['result'] = "抱歉，生成提示词时出现错误。"

        return super().handle(context)

    def _remove_empty_lines(self, text):
        """去除文本中的空行（包括只含空白字符的行）

        Args:
            text: 输入文本

        Returns:
            str: 清洗后的文本
        """
        if not text:
            return ""

        lines = text.splitlines()
        cleaned_lines = [line.rstrip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)
        
    def _save_user_input_history(self, context: Dict[str, Any]) -> None:
        """
        保存用户输入作为历史记录，供下次请求使用

        Args:
            context: 当前上下文
        """
        try:
            user_id = context.get('user_id')
            if not user_id:
                logger.warning("用户ID不存在，无法保存历史记录")
                return

            # 获取当前用户输入
            current_input = context.get('input_text', '')
            
            # 构建缓存键
            input_cache_key = f"context_input:{user_id}"
            
            # 获取现有的历史记录
            history_inputs = self.cache.get(input_cache_key) or []
            
            # 如果历史记录不是列表格式，则初始化为空列表
            if not isinstance(history_inputs, list):
                history_inputs = []
            
            # 添加当前输入到历史记录
            history_inputs.append({
                'input': current_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # 限制历史记录数量，只保留最近的5条记录
            if len(history_inputs) > 5:
                history_inputs = history_inputs[-5:]
            
            # 保存到缓存，不设置过期时间
            self.cache.set(input_cache_key, history_inputs)
            
            logger.info(f"已保存用户输入历史记录，用户ID: {user_id}")
            
        except Exception as e:
            logger.warning(f"保存用户输入历史记录失败: {e}")
