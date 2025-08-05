from typing import Dict, Any
from slot.SlotHandler import SlotHandler

class TokenizationSlotHandler(SlotHandler):
    """分词处理器"""

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取分词器并进行分词
        from dict.ltp_tokenizer import get_tokenizer
        tokenizer = get_tokenizer()
        context['tokenizer'] = tokenizer
        context['tokenized_text'] = tokenizer.tokenize(context['cleaned_text'])
        return super().handle(context)