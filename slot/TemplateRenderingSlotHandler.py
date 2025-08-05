from typing import Dict, Any
from slot.SlotHandler import SlotHandler

class TemplateRenderingSlotHandler(SlotHandler):
    """模板渲染槽位处理器"""

    def __init__(self, builder, next_handler=None):
        super().__init__(next_handler)
        self.builder = builder

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 渲染模板
        rendered_prompt = self.builder.template_manager.get_template(
            context['template_name'],
            lang=context['language'],
            **context['context_dict']
        )

        # 清洗最终结果
        context['result'] = self.builder.remove_empty_lines(rendered_prompt)
        return super().handle(context)