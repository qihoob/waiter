import yaml
import os
from jinja2 import Template

class PromptTemplateLoader:
    def __init__(self, file_path: str, slot_dict: dict = None):
        """
        初始化模板加载器

        :param file_path: YAML 模板文件路径
        :param slot_dict: 槽位字典，用于校验参数合法性
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"模板文件不存在: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            self.templates = yaml.safe_load(f).get("templates", {})

        self.slot_dict = slot_dict or {}

    def validate_slot(self, key: str, value: str):
        """
        校验值是否属于 SLOT_DICT 中指定的槽位值
        """
        if key in self.slot_dict and value not in self.slot_dict[key]:
            raise ValueError(f"值 '{value}' 不在槽位 '{key}' 的允许范围内")

    def get_template(self, template_name: str, lang: str = "zh-CN", **kwargs):
        """
        获取指定模板并替换变量（使用 Jinja2 引擎）
        """
        if template_name not in self.templates:
            raise KeyError(f"未找到模板: {template_name}")

        template_data = self.templates[template_name]

        if lang not in template_data:
            raise KeyError(f"模板 {template_name} 不支持语言: {lang}")

        template_str = template_data[lang]

        # 使用 Jinja2 渲染模板
        jinja_template = Template(template_str)
        return jinja_template.render(**kwargs)

    def get_template_by_slot(self, template_name: str, lang: str = "zh-CN", **kwargs):
        """
        使用 SLOT_DICT 校验并填充模板变量

        :param template_name: 模板名称
        :param lang: 语言
        :param kwargs: 参数
        :return: 替换后的模板
        """
        for key, value in kwargs.items():
            if isinstance(value, str):
                self.validate_slot(key, value)

        return self.get_template(template_name, lang=lang, **kwargs)

    def list_templates(self):
        """
        列出所有可用模板名称
        """
        return list(self.templates.keys())

