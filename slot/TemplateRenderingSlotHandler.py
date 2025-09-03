# E:\work\waiter\slot\TemplateRenderingSlotHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import logging
from slot.global_vars import get_global_template_manager

logger = logging.getLogger(__name__)

class TemplateRenderingSlotHandler(SlotHandler):
    """模板渲染槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

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
