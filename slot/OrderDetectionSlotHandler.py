# E:\work\waiter\slot\OrderDetectionSlotHandler.py
"""
订单检测槽位处理器
"""

from typing import Dict, Any, List
from slot.SlotHandler import SlotHandler
from prompt_builder.config import ORDER_KEYWORDS
import re


class OrderDetectionSlotHandler(SlotHandler):
    """订单检测槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从ORDER_KEYWORDS中获取订单关键词
        self.order_keywords = ORDER_KEYWORDS
        # 按长度排序，优先匹配长词汇
        self.order_keywords.sort(key=len, reverse=True)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)
        
        if text_to_process:
            # 检测订单意图
            is_order_intent = self._detect_order_intent(text_to_process)
            
            # 将订单意图添加到context中
            context['is_order'] = is_order_intent
            
            # 如果检测到订单意图，也可以在slots中添加相关信息
            if is_order_intent:
                slots = context.setdefault('slots', {})
                slots['订单状态'] = "下单意图"
        
        return super().handle(context)

    def _get_text_to_process(self, context: Dict[str, Any]) -> str:
        """
        获取需要处理的文本
        
        Args:
            context: 处理上下文
            
        Returns:
            需要处理的文本
        """
        # 按优先级获取文本
        text_sources = [
            context.get('cleaned_text'),
            context.get('input_text'),
            context.get('tokenized_text')
        ]
        
        for text in text_sources:
            if text:
                return text
                
        return ""

    def _detect_order_intent(self, text: str) -> bool:
        """
        从文本中检测订单意图
        
        Args:
            text: 输入文本
            
        Returns:
            是否检测到订单意图
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()
        
        # 查找匹配的订单关键词
        for keyword in self.order_keywords:
            # 将关键词也转为小写进行匹配
            keyword_lower = keyword.lower()
            
            # 精确匹配整个词
            if keyword_lower in processed_text:
                return True  # 检测到订单意图
                
        return False


# 测试代码
def test_order_detection_slot_handler():
    """测试订单检测槽位处理器"""
    print("=" * 50)
    print("测试订单检测槽位处理器")
    print("=" * 50)
    
    # 创建处理器实例
    handler = OrderDetectionSlotHandler()
    
    # 测试用例
    test_cases = [
        {
            "name": "识别点菜意图",
            "context": {
                "cleaned_text": "我想点菜，来一份宫保鸡丁"
            }
        },
        {
            "name": "识别订位意图",
            "context": {
                "cleaned_text": "我要订位，明天晚上六点"
            }
        },
        {
            "name": "识别已下单意图",
            "context": {
                "cleaned_text": "我已经订好了，明天来取"
            }
        },
        {
            "name": "无订单意图",
            "context": {
                "cleaned_text": "我想了解一下你们的菜品"
            }
        },
        {
            "name": "复杂订单意图",
            "context": {
                "cleaned_text": "我要下单，准备点菜了"
            }
        }
    ]
    
    # 执行测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"输入文本: {test_case['context']['cleaned_text']}")
        
        try:
            # 执行处理
            result_context = handler.handle(test_case['context'].copy())
            
            # 输出结果
            is_order = result_context.get('is_order', False)
            print(f"检测到订单意图: {is_order}")
            
            slots = result_context.get('slots', {})
            order_status = slots.get('订单状态', '未下单')
            print(f"订单状态: {order_status}")
            
        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_order_detection_slot_handler()
