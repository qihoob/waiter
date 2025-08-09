# E:\work\waiter\slot\SlotValidationHandler.py
from typing import Dict, Any, List, Set
from slot.SlotHandler import SlotHandler
import logging

logger = logging.getLogger(__name__)

class SlotValidationHandler(SlotHandler):
    """槽位验证处理器，根据意图检查相应的槽位是否已填写"""

    def __init__(self, next_handler=None):
        """
        初始化槽位验证处理器

        Args:
            next_handler: 下一个处理器
        """
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

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            slots = context.get('slots', {})

            # 获取意图和该意图需要的槽位
            intent = context.get('intent', 'default')
            required_slots = self._get_required_slots_for_intent(intent)

            # 检查缺失的关键槽位
            missing_slots = self._validate_required_slots(slots, required_slots)

            if missing_slots:
                # 如果有缺失的槽位，设置提示信息
                context['missing_slots'] = missing_slots
                context['need_user_input'] = True
                context['prompt_message'] = self._generate_prompt_message(missing_slots, intent)

                logger.info(f"意图 '{intent}' 需要槽位 {required_slots}，缺失槽位: {missing_slots}")
            else:
                # 所有关键槽位都已填写
                context['need_user_input'] = False

        except Exception as e:
            logger.error(f"槽位验证过程中出错: {e}")

        return super().handle(context)

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

    def _validate_required_slots(self, slots: Dict[str, Any], required_slots: Set[str]) -> List[str]:
        """
        验证必需的槽位是否存在

        Args:
            slots: 已提取的槽位字典
            required_slots: 当前意图需要的槽位集合

        Returns:
            List[str]: 缺失的槽位列表
        """
        missing_slots = []

        for slot_name in required_slots:
            # 检查槽位是否存在且不为空
            if slot_name not in slots or not slots[slot_name]:
                missing_slots.append(slot_name)

        return missing_slots

    def _generate_prompt_message(self, missing_slots: List[str], intent: str) -> str:
        """
        生成提示用户输入的消息

        Args:
            missing_slots: 缺失的槽位列表
            intent: 用户意图

        Returns:
            str: 提示消息
        """
        # 根据意图定制提示消息
        intent_messages = {
            "order_food": "为了更好地为您点餐",
            "recommend_dish": "为了更好地为您推荐菜品",
            "query_nutrition": "为了更好地为您提供营养建议",
            "recommend_game": "为了更好地为您推荐游戏",
            "play_game": "为了更好地为您安排游戏",
            "order_drink": "为了更好地为您点饮品",
            "recommend_drink": "为了更好地为您推荐饮品",
            "festival_recommend": "为了更好地为您推荐节日活动",
            "default": "为了更好地为您服务"
        }

        intent_message = intent_messages.get(intent, intent_messages["default"])

        slot_prompts = {
            "场景": "请问您是在什么场景下用餐？(例如: 朋友聚会、家庭聚餐、商务宴请等)",
            "人数": "请问有多少人用餐？",
            "菜系": "您想吃什么菜系？(例如: 川菜、粤菜、日料等)",
            "口味": "您偏好什么口味？(例如: 辣味、清淡、酸甜等)",
            "健康偏好": "您有什么健康偏好？(例如: 低脂、高蛋白、无糖等)",
            "忌口": "您有什么忌口的食物吗？",
            "过敏原": "您对什么食物过敏？",
            "游戏": "您想玩什么游戏？",
            "饮品": "您想喝什么饮品？",
            "节日": "您想了解哪个节日的活动？"
        }

        messages = [slot_prompts.get(slot, f"请提供{slot}信息") for slot in missing_slots]
        return f"{intent_message}，请提供以下信息:\n" + "\n".join(messages)


# 测试代码
def test_slot_validation_handler():
    """测试槽位验证处理器"""
    print("=" * 50)
    print("测试槽位验证处理器")
    print("=" * 50)

    # 创建验证器实例
    validator = SlotValidationHandler()

    # 测试用例
    test_cases = [
        {
            "name": "点餐意图-缺失菜系和口味",
            "intent": "order_food",
            "slots": {
                "场景": "朋友聚会",
                "人数": "4人",
                "健康偏好": "低脂"
                # 缺失菜系和口味
            }
        },
        {
            "name": "推荐游戏意图-缺失所有槽位",
            "intent": "recommend_game",
            "slots": {
                # 所有槽位都缺失
            }
        },
        {
            "name": "营养查询意图-缺失忌口和过敏原",
            "intent": "query_nutrition",
            "slots": {
                "健康偏好": "低脂"
                # 缺失忌口和过敏原
            }
        },
        {
            "name": "点饮品意图-完整槽位",
            "intent": "order_drink",
            "slots": {
                "饮品": "可乐",
                "人数": "2人"
            }
        },
        {
            "name": "默认意图-缺失场景",
            "intent": "default",
            "slots": {
                "人数": "3人"
                # 缺失场景
            }
        }
    ]

    # 执行测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"意图: {test_case['intent']}")
        print(f"当前槽位: {test_case['slots']}")

        try:
            # 构建测试上下文
            context = {
                'intent': test_case['intent'],
                'slots': test_case['slots']
            }

            # 获取该意图需要的槽位
            required_slots = validator._get_required_slots_for_intent(test_case['intent'])
            print(f"需要的槽位: {required_slots}")

            # 验证缺失的槽位
            missing_slots = validator._validate_required_slots(test_case['slots'], required_slots)
            print(f"缺失的槽位: {missing_slots}")

            # 生成提示消息
            if missing_slots:
                prompt_message = validator._generate_prompt_message(missing_slots, test_case['intent'])
                print(f"提示消息:\n{prompt_message}")
            else:
                print("所有槽位都已填写完整")

        except Exception as e:
            print(f"处理出错: {e}")

    # 测试处理链
    print("\n" + "=" * 30)
    print("测试处理链")
    print("=" * 30)

    test_contexts = [
        {
            "name": "需要用户输入的上下文",
            "context": {
                'intent': 'order_food',
                'slots': {
                    "场景": "家庭聚餐",
                    "人数": "5人"
                    # 缺失菜系、口味、健康偏好
                }
            }
        },
        {
            "name": "完整槽位的上下文",
            "context": {
                'intent': 'order_drink',
                'slots': {
                    "饮品": "咖啡",
                    "人数": "1人"
                }
            }
        }
    ]

    for i, test_case in enumerate(test_contexts, 1):
        print(f"\n处理链测试 {i}: {test_case['name']}")

        try:
            # 复制上下文以避免修改原始数据
            context = test_case['context'].copy()

            # 执行处理
            result_context = validator.handle(context)

            need_user_input = result_context.get('need_user_input', False)
            print(f"需要用户输入: {need_user_input}")

            if need_user_input:
                missing_slots = result_context.get('missing_slots', [])
                prompt_message = result_context.get('prompt_message', '')
                print(f"缺失槽位: {missing_slots}")
                print(f"提示消息:\n{prompt_message}")
            else:
                print("槽位完整，无需用户输入")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_slot_validation_handler()
