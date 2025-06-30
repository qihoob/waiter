import yaml
import jinja2

class PromptTemplateManager:
    def __init__(self, yaml_path="collector/templates/prompt_templates.yaml"):
        self.env = jinja2.Environment()
        with open(yaml_path, 'r', encoding='utf-8') as f:
            self.templates = yaml.safe_load(f)

    def render(self, template_keys: list, slots: dict) -> str:
        rendered = []
        for key in template_keys:
            if key in self.templates:
                tpl = self.env.from_string(self.templates[key])
                rendered.append(tpl.render(**slots))
        return " ".join(rendered)

    def list_templates(self):
        return list(self.templates.keys())