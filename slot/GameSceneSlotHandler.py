# E:\work\waiter\slot\GameSceneSlotHandler.py
"""
游戏场景槽位处理器
"""

from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.config import GAME_RECOMMENDATION_RULES, SLOT_DICT
import re


class GameSceneSlotHandler(SlotHandler):
    """游戏场景槽位处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 从SLOT_DICT中获取场景词典
        self.scene_keywords = SLOT_DICT.get("场景", [])
        # 按长度排序，优先匹配长词汇
        self.scene_keywords.sort(key=len, reverse=True)
        # 保存游戏推荐规则
        self.game_recommendation_rules = GAME_RECOMMENDATION_RULES

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # 获取需要处理的文本
        text_to_process = self._get_text_to_process(context)
        
        if text_to_process:
            # 提取场景信息
            scene_info = self._extract_scene_info(text_to_process)
            
            # 将场景信息添加到slots中
            slots = context.setdefault('slots', {})
            
            # 如果提取到场景信息，则更新slots
            if scene_info:
                slots['场景'] = scene_info
                
                # 根据场景推荐游戏
                recommended_games = self._get_recommended_games(scene_info)
                if recommended_games:
                    slots['推荐游戏'] = recommended_games
        
        return super().handle(context)

    def _get_text_to_process(self, context: Dict[str, Any]) -> Optional[str]:
        """
        获取需要处理的文本
        
        Args:
            context: 处理上下文
            
        Returns:
            需要处理的文本，如果没有则返回None
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
                
        return None

    def _extract_scene_info(self, text: str) -> Optional[str]:
        """
        从文本中提取场景信息
        
        Args:
            text: 输入文本
            
        Returns:
            识别到的场景，如果没有则返回None
        """
        # 预处理文本：转为小写，去除多余空格
        processed_text = text.lower().strip()
        
        # 查找匹配的场景
        for scene in self.scene_keywords:
            # 将场景名称也转为小写进行匹配
            scene_lower = scene.lower()
            
            # 精确匹配整个词
            if scene_lower in processed_text:
                return scene  # 返回原始大小写的场景名称
                
        return None

    def _get_recommended_games(self, scene: str) -> Optional[List[str]]:
        """
        根据场景获取推荐游戏列表
        
        Args:
            scene: 场景名称
            
        Returns:
            推荐游戏列表，如果没有则返回None
        """
        # 查找匹配的场景并返回推荐游戏
        for scene_key, games in self.game_recommendation_rules.items():
            # 将场景名称也转为小写进行匹配
            if scene_key.lower() in scene.lower():
                return games
                
        return None


# 测试代码
def test_game_scene_slot_handler():
    """测试游戏场景槽位处理器"""
    print("=" * 50)
    print("测试游戏场景槽位处理器")
    print("=" * 50)
    
    # 创建处理器实例
    handler = GameSceneSlotHandler()
    
    # 测试用例
    test_cases = [
        {
            "name": "识别朋友聚会场景",
            "context": {
                "cleaned_text": "我们朋友聚会想玩点游戏"
            }
        },
        {
            "name": "识别家庭聚餐场景",
            "context": {
                "cleaned_text": "一家人聚餐时玩什么游戏好"
            }
        },
        {
            "name": "识别情侣约会场景",
            "context": {
                "cleaned_text": "情侣约会时可以玩的游戏"
            }
        },
        {
            "name": "识别公司年会场景",
            "context": {
                "cleaned_text": "公司年会需要一些团建游戏"
            }
        },
        {
            "name": "无场景描述",
            "context": {
                "cleaned_text": "我想吃火锅"
            }
        },
        {
            "name": "多种场景选择第一个",
            "context": {
                "cleaned_text": "朋友聚会或者家庭聚餐时玩什么"
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
            slots = result_context.get('slots', {})
            scene = slots.get('场景', '未提取到')
            print(f"提取的场景: {scene}")
            
            recommended_games = slots.get('推荐游戏', '无推荐')
            print(f"推荐游戏: {recommended_games}")
            
        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_game_scene_slot_handler()
