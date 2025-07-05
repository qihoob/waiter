import yaml
from jinja2 import Environment, meta
import os

class PromptTemplateLoader:
    def __init__(self, template_file_path):
        with open(template_file_path, 'r', encoding='utf-8') as f:
            self.templates = yaml.safe_load(f)

    def get_template(self, template_name, lang='zh-CN', **kwargs):
        """
        获取并渲染模板
        :param template_name: 模板名称
        :param lang: 语言版本
        :param kwargs: 上下文参数
        :return: 渲染后的提示词
        """
        if template_name not in self.templates:
            raise ValueError(f"模板 {template_name} 不存在")

        if lang not in self.templates[template_name]:
            raise ValueError(f"模板 {template_name} 不支持语言 {lang}")

        raw_template = self.templates[template_name][lang]
        used_vars = self._extract_used_variables(raw_template)

        # 过滤掉模板中没有使用的变量
        filtered_context = {
            k: v for k, v in kwargs.items() if k in used_vars or k.startswith('_')
        }

        # 渲染模板
        env = Environment()
        template = env.from_string(raw_template)
        return template.render(**filtered_context)

    def _extract_used_variables(self, template_str):
        """
        提取模板中使用的变量名
        :param template_str: 模板字符串
        :return: set of variable names
        """
        env = Environment()
        ast = env.parse(template_str)
        return meta.find_undeclared_variables(ast)
