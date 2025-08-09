# E:\work\waiter\slot\IntentBasedSlotSelector.py
from typing import Dict, Any, List, Set, Optional
from slot.SlotHandler import SlotHandler
import logging

# 导入全局变量管理模块
from slot.global_vars import get_global_intent_classifier

logger = logging.getLogger(__name__)

class IntentBasedSlotSelector(SlotHandler):
    """基于意图的槽位选择器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)

        # 定义不同意图需要的槽位
        self.intent_required_slots = {
            # 餐饮相关意图
            "order_food": {"菜系", "人数", "场景", "口味", "健康偏好"},
            "recommend_dish": {"菜系", "人数", "场景", "口味", "健康偏好"},
            "query_nutrition": {"健康偏好", "忌口", "过敏原"},

            # 游戏相关意图
            "recommend_game": {"场景", "人数", "游戏"},
            "play_game": {"游戏", "人数"},

            # 饮品相关意图
            "order_drink": {"饮品", "人数"},
            "recommend_drink": {"饮品", "场景"},

            # 节日相关意图
            "festival_recommend": {"节日", "场景", "人数"},

            # 默认意图需要的槽位
            "default": {"场景", "人数"},
            "enhanced_basic_with_all": {"菜系", "人数", "场景", "口味", "健康偏好"}
        }

        # 定义槽位到处理器的映射
        self.slot_handler_mapping = {
            "菜系": "CuisineSlotHandler",
            "人数": "PeopleCountSlotHandler",
            "场景": "SceneSlotHandler",
            "口味": "TasteSlotHandler",
            "健康偏好": "HealthPreferenceSlotHandler",
            "忌口": "DietaryRestrictionSlotHandler",
            "过敏原": "AllergenSlotHandler",
            "游戏": "GameSlotHandler",
            "饮品": "DrinkSlotHandler",
            "节日": "FestivalSlotHandler"
        }

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 如果上下文中还没有意图，则进行意图识别
            if 'intent' not in context or not context['intent']:
                intent = self._classify_intent(context)
                context['intent'] = intent
                logger.info(f"识别到用户意图: {intent}")

            # 获取该意图需要的槽位
            intent = context.get('intent', 'default')
            required_slots = self._get_required_slots_for_intent(intent)
            context['required_slots'] = required_slots

            logger.info(f"意图 '{intent}' 需要的槽位: {required_slots}")

        except Exception as e:
            logger.warning(f"意图槽位选择过程中出错: {e}")
            # 设置默认意图和槽位
            context['intent'] = 'default'
            context['required_slots'] = self.intent_required_slots.get("default", set()).copy()

        return super().handle(context)

    def _classify_intent(self, context: Dict[str, Any]) -> str:
        """
        使用全局意图分类器识别用户意图

        Args:
            context: 处理上下文

        Returns:
            str: 识别到的意图
        """
        try:
            # 获取全局意图分类器
            intent_classifier = get_global_intent_classifier()

            if not intent_classifier:
                logger.warning("意图分类器未初始化，使用默认意图")
                return "default"

            # 获取需要处理的文本
            text_to_process = self._get_text_to_process(context)

            if not text_to_process:
                logger.warning("没有可处理的文本，使用默认意图")
                return "default"

            # 使用意图分类器进行分类
            # 检查是否是机器学习分类器（具有classify方法）
            if hasattr(intent_classifier, 'classify'):
                intent = intent_classifier.classify(text_to_process)
            # 否则假设是规则分类器（具有predict方法）
            elif hasattr(intent_classifier, 'predict'):
                intent = intent_classifier.predict(text_to_process)
            else:
                logger.warning("意图分类器不支持classify或predict方法，使用默认意图")
                return "default"

            return intent

        except Exception as e:
            logger.warning(f"意图分类过程中出错: {e}")
            return "default"

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

    def _get_required_slots_for_intent(self, intent: str) -> Set[str]:
        """
        根据意图获取需要的槽位集合

        Args:
            intent: 用户意图

        Returns:
            Set[str]: 需要的槽位集合
        """
        # 精确匹配意图
        if intent in self.intent_required_slots:
            return self.intent_required_slots[intent].copy()

        # 模糊匹配意图（前缀匹配）
        for intent_prefix, slots in self.intent_required_slots.items():
            if intent.startswith(intent_prefix):
                return slots.copy()

        # 返回默认槽位
        return self.intent_required_slots.get("default", set()).copy()

    def get_handlers_for_intent(self, intent: str) -> List[str]:
        """
        根据意图获取需要的处理器列表

        Args:
            intent: 用户意图

        Returns:
            List[str]: 需要的处理器列表
        """
        required_slots = self._get_required_slots_for_intent(intent)
        handlers = []

        for slot in required_slots:
            if slot in self.slot_handler_mapping:
                handler = self.slot_handler_mapping[slot]
                if handler not in handlers:
                    handlers.append(handler)

        return handlers

    def is_slot_required_for_intent(self, intent: str, slot: str) -> bool:
        """
        检查特定槽位是否为特定意图所必需

        Args:
            intent: 用户意图
            slot: 槽位名称

        Returns:
            bool: 是否必需
        """
        required_slots = self._get_required_slots_for_intent(intent)
        return slot in required_slots


# 测试代码
def test_intent_based_slot_selector():
    """测试意图槽位选择器"""
    print("=" * 50)
    print("测试意图槽位选择器")
    print("=" * 50)

    # 创建选择器实例
    selector = IntentBasedSlotSelector()

    # 测试用例
    test_cases = [
        {
            "name": "点餐意图",
            "intent": "order_food",
            "context": {
                "intent": "order_food",
                "cleaned_text": "我想点一份川菜，4个人吃"
            }
        },
        {
            "name": "推荐菜品意图",
            "intent": "recommend_dish",
            "context": {
                "intent": "recommend_dish",
                "cleaned_text": "推荐一些适合夏天的清爽菜品"
            }
        },
        {
            "name": "游戏推荐意图",
            "intent": "recommend_game",
            "context": {
                "intent": "recommend_game",
                "cleaned_text": "朋友聚会想玩游戏，推荐一下"
            }
        },
        {
            "name": "营养查询意图",
            "intent": "query_nutrition",
            "context": {
                "intent": "query_nutrition",
                "cleaned_text": "有什么适合减肥的餐品"
            }
        },
        {
            "name": "未知意图",
            "intent": "unknown_intent",
            "context": {
                "intent": "unknown_intent",
                "cleaned_text": "随便聊聊"
            }
        }
    ]

    # 执行测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"意图: {test_case['intent']}")

        try:
            # 测试获取需要的槽位
            required_slots = selector._get_required_slots_for_intent(test_case['intent'])
            print(f"需要的槽位: {required_slots}")

            # 测试获取需要的处理器
            required_handlers = selector.get_handlers_for_intent(test_case['intent'])
            print(f"需要的处理器: {required_handlers}")

            # 测试特定槽位是否必需
            is_cuisine_required = selector.is_slot_required_for_intent(test_case['intent'], "菜系")
            print(f"菜系槽位是否必需: {is_cuisine_required}")

            # 测试处理上下文
            result_context = selector.handle(test_case['context'].copy())
            print(f"识别到的意图: {result_context.get('intent', '未设置')}")
            print(f"上下文中记录的必需槽位: {result_context.get('required_slots', '未设置')}")

        except Exception as e:
            print(f"处理出错: {e}")

    # 测试前缀匹配
    print("\n" + "=" * 30)
    print("测试前缀匹配")
    print("=" * 30)

    prefix_test_cases = [
        ("order_food_special", "点餐特殊意图"),
        ("recommend_dish_vegetarian", "推荐素食菜品意图"),
        ("play_game_online", "在线游戏意图")
    ]

    for intent, description in prefix_test_cases:
        print(f"\n{description}: {intent}")
        required_slots = selector._get_required_slots_for_intent(intent)
        print(f"匹配到的槽位: {required_slots}")


if __name__ == "__main__":
    test_intent_based_slot_selector()
