# E:\work\waiter\slot\TokenizationSlotHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
import re

class TokenizationSlotHandler(SlotHandler):
    """分词处理器"""

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取全局分词器并进行分词
        from slot.global_vars import get_global_tokenizer
        tokenizer = get_global_tokenizer()
        context['tokenizer'] = tokenizer

        # 使用自定义分词方法处理文本
        context['tokenized_text'] = self._custom_tokenize(context['cleaned_text'])
        return super().handle(context)

    def _custom_tokenize(self, text: str) -> str:
        """
        自定义分词方法，处理数字与单位连写的情况

        Args:
            text: 清洗后的文本

        Returns:
            str: 分词后的文本
        """
        from slot.global_vars import get_global_tokenizer
        tokenizer = get_global_tokenizer()

        # 首先进行常规分词
        tokens = tokenizer.tokenize(text)

        # 处理数字与单位连写的情况（如"4人"、"200元"等）
        processed_tokens = []
        i = 0
        while i < len(tokens):
            token = tokens[i]

            # 检查是否是数字+单位的组合（如"4人"）
            if i < len(tokens) - 1:
                # 检查当前token是否为数字，下一个token是否为单位词
                if self._is_number_token(token) and self._is_unit_token(tokens[i+1]):
                    # 合并数字和单位为一个token
                    combined_token = token + tokens[i+1]
                    processed_tokens.append(combined_token)
                    i += 2  # 跳过下一个token
                    continue

            # 检查单个token中是否包含数字和单位（如"4人"作为一个token）
            if self._contains_number_and_unit(token):
                # 保持原样，因为已经是一个完整的token
                processed_tokens.append(token)
            else:
                processed_tokens.append(token)

            i += 1

        return ' '.join(processed_tokens)

    def _is_number_token(self, token: str) -> bool:
        """判断是否为数字token"""
        return bool(re.match(r'^\d+$', token))

    def _is_unit_token(self, token: str) -> bool:
        """判断是否为单位token"""
        unit_tokens = ['人', '位', '份', '餐', '杯', '瓶', '盘', '碗', '元']
        return token in unit_tokens

    def _contains_number_and_unit(self, token: str) -> bool:
        """判断token是否包含数字和单位"""
        # 检查是否包含数字和单位的组合
        return bool(re.match(r'^\d+[人位份餐杯瓶盘碗元]$', token))
