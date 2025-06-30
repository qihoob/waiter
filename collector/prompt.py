# prompt.py
import jieba

from constant.constant import MAX_INPUT_LENGTH, SUPPORTED_LANGUAGES
from template.templates import TemplateManager

# 加载自定义词典（路径根据实际情况调整）
jieba.load_userdict("collector/custom_dict.txt")


class PromptBuilder:
    def __init__(self, max_length=MAX_INPUT_LENGTH):
        self.max_length = max_length
        self.template_manager = TemplateManager()
        self.default_language = 'zh-CN'

    def build_prompt(self, input_text, **kwargs):
        """
        构建标准提示词
        :param input_text: 用户输入文本
        :param kwargs: 其他构建参数，如language（语言）, template_name（模板名称）, context（上下文）等
        :return: 构建好的提示词
        """
        # 输入验证和清理
        cleaned_text = self._clean_input(input_text)

        # 文本预处理
        processed_text = self._preprocess_text(cleaned_text)

        # 获取参数
        language = kwargs.get('language', self.default_language)
        template_name = kwargs.get('template_name', 'basic')
        context = kwargs.get('context', None)

        # 构建提示词模板
        if context:
            prompt = self.template_manager.apply_context_template(processed_text, context, language, template_name)
        else:
            prompt = self.template_manager.apply_template(processed_text, language, template_name)

        return prompt

    def _clean_input(self, text):
        """清理输入文本"""
        if not text:
            return ""

        # 去除首尾空白字符
        text = text.strip()

        # 限制最大长度
        if len(text) > self.max_length:
            text = text[:self.max_length]

        return text

    def _preprocess_text(self, text):
        """文本预处理"""
        # 添加中文分词支持（示例）
        if self._is_chinese(text):
            text = self._chinese_tokenize(text)

        return text

    def _is_chinese(self, text):
        """检查是否包含中文"""
        import re
        return bool(re.search(u'[\u4e00-\u9fff]', text))

    def _chinese_tokenize(self, text):
        """中文分词（示例实现，可替换为专业分词库如jieba）"""
        # 这里使用简单的按字分割作为示例
        return  " ".join(jieba.cut(text))
