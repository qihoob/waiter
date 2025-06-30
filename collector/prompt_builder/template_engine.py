from jinja2 import Template
from collector.prompt_builder.config import TEMPLATES

def render_prompt(prompt_input: dict) -> str:
    intent_type = prompt_input["intent"]["intent_type"]
    template_str = TEMPLATES.get(intent_type)
    if not template_str:
        raise ValueError(f"No template for intent type: {intent_type}")
    template = Template(template_str)
    return template.render(**prompt_input)
