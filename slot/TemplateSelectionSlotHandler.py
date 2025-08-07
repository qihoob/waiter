# E:\work\waiter\slot\TemplateSelectionSlotHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
from prompt_builder.config import INTENT_TO_TEMPLATE_MAP
import logging

logger = logging.getLogger(__name__)

class TemplateSelectionSlotHandler(SlotHandler):
    """模板选择槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 根据意图选择模板
            intent = context.get('intent')
            kwargs = context.get('kwargs', {})

            context['template_name'] = self._select_template(kwargs, intent)
            logger.info(f"选择模板: {context['template_name']}")
        except Exception as e:
            logger.error(f"模板选择失败: {e}")
            context['template_name'] = "enhanced_basic_with_all"

        return super().handle(context)

    def _select_template(self, kwargs, intent):
        """根据意图选择模板

        Args:
            kwargs: 其他参数
            intent: 用户意图

        Returns:
            str: 选择的模板名称
        """
        template_name = kwargs.get("template_name")
        if template_name:
            return template_name

        try:
            selected = INTENT_TO_TEMPLATE_MAP.get(intent, "enhanced_basic_with_all")
            logger.info(f"根据意图 '{intent}' 选择了模板 '{selected}'")
            return selected
        except Exception as e:
            logger.warning(f"意图分类失败，使用默认模板: {e}")
            return "enhanced_basic_with_all"
