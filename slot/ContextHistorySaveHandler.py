# E:\work\waiter\slot\ContextValidationAndHistoryHandler.py
from typing import Dict, Any, List, Set
from slot.SlotHandler import SlotHandler, SlotHandlerInterrupt
import logging
from memory.local_cache import GlobalCache
from datetime import datetime

logger = logging.getLogger(__name__)

class ContextHistorySaveHandler(SlotHandler):
    """上下文验证和历史保存处理器，根据意图验证槽位并在缺失时保存上下文"""

    def __init__(self, next_handler=None, cache_expire_time=300):
        """
        初始化上下文验证和历史保存处理器

        Args:
            next_handler: 下一个处理器
            cache_expire_time: 缓存过期时间（秒），默认5分钟
        """
        super().__init__(next_handler)
        self.cache = GlobalCache.get_instance()
        self.cache_expire_time = cache_expire_time

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
        user_id = context.get('user_id')
        session_id = context.get('session_id')

        slots = context.get('slots', {})

        # 获取意图和该意图需要的槽位
        intent = context.get('intent', 'default')
        required_slots = self._get_required_slots_for_intent(intent)

        # 检查缺失的关键槽位
        missing_slots = self._validate_required_slots(slots, required_slots)

        # 如果有缺失的槽位且有用户ID和会话ID，则保存上下文
        if missing_slots and user_id and session_id:
            # 保存当前上下文到缓存
            self._save_context_to_history(user_id, session_id, context)
            logger.info(f"已保存上下文历史，用户ID: {user_id}, 会话ID: {session_id}")

            # 设置提示信息
            context['missing_slots'] = missing_slots
            context['need_user_input'] = True
            context['prompt_message'] = self._generate_prompt_message(missing_slots, intent)

            # 中断处理链，等待用户补充信息
            raise SlotHandlerInterrupt(context)
        elif not missing_slots:
            # 所有关键槽位都已填写
            context['need_user_input'] = False

        # 继续处理链
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

    def _save_context_to_history(self, user_id: str, session_id: str, context: Dict[str, Any]):
        """
        将当前上下文保存到历史记录中

        Args:
            user_id: 用户ID
            session_id: 会话ID
            context: 当前上下文
        """
        try:
            cache_key = f"context_history:{user_id}:{session_id}"

            # 过滤需要保存的上下文字段
            context_to_save = {
                'slots': context.get('slots', {}),
                'location': context.get('location'),
                'location_info': context.get('location_info'),
                'weather_info': context.get('weather_info'),
                'order_history': context.get('order_history', []),
                'played_games': context.get('played_games', []),
                'input_text': context.get('input_text'),
                'is_order': context.get('is_order', False),
                'intent': context.get('intent'),
                'timestamp': datetime.now().timestamp()
            }

            # 保存到缓存
            self.cache.set(cache_key, context_to_save, self.cache_expire_time)
        except Exception as e:
            logger.warning(f"保存上下文历史失败: {e}")

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
def test_context_validation_and_history_handler():
    """测试上下文验证和历史保存处理器"""
    print("=" * 60)
    print("测试上下文验证和历史保存处理器")
    print("=" * 60)

    # 创建处理器实例
    handler = ContextHistorySaveHandler()

    # 测试用例
    test_cases = [
        {
            "name": "点餐意图-缺失菜系和口味",
            "context": {
                'user_id': 'test_user_1',
                'session_id': 'session_1',
                'intent': 'order_food',
                'slots': {
                    "场景": "朋友聚会",
                    "人数": "4人",
                    "健康偏好": "低脂"
                    # 缺失菜系和口味
                }
            }
        },
        {
            "name": "推荐游戏意图-缺失所有槽位",
            "context": {
                'user_id': 'test_user_2',
                'session_id': 'session_2',
                'intent': 'recommend_game',
                'slots': {
                    # 所有槽位都缺失
                }
            }
        },
        {
            "name": "营养查询意图-缺失忌口和过敏原",
            "context": {
                'user_id': 'test_user_3',
                'session_id': 'session_3',
                'intent': 'query_nutrition',
                'slots': {
                    "健康偏好": "低脂"
                    # 缺失忌口和过敏原
                }
            }
        },
        {
            "name": "点饮品意图-完整槽位",
            "context": {
                'user_id': 'test_user_4',
                'session_id': 'session_4',
                'intent': 'order_drink',
                'slots': {
                    "饮品": "可乐",
                    "人数": "2人"
                }
            }
        },
        {
            "name": "默认意图-缺失场景",
            "context": {
                'user_id': 'test_user_5',
                'session_id': 'session_5',
                'intent': 'default',
                'slots': {
                    "人数": "3人"
                    # 缺失场景
                }
            }
        },
        {
            "name": "无用户ID的情况",
            "context": {
                'intent': 'order_food',
                'slots': {
                    "场景": "朋友聚会",
                    "人数": "4人",
                    "健康偏好": "低脂"
                    # 缺失菜系和口味，但没有用户ID
                }
            }
        }
    ]

    # 执行测试
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"意图: {test_case['context'].get('intent', 'default')}")
        print(f"用户ID: {test_case['context'].get('user_id', '无')}")
        print(f"当前槽位: {test_case['context'].get('slots', {})}")

        try:
            # 获取该意图需要的槽位
            intent = test_case['context'].get('intent', 'default')
            required_slots = handler._get_required_slots_for_intent(intent)
            print(f"需要的槽位: {required_slots}")

            # 验证缺失的槽位
            slots = test_case['context'].get('slots', {})
            missing_slots = handler._validate_required_slots(slots, required_slots)
            print(f"缺失的槽位: {missing_slots}")

            # 测试处理
            try:
                result_context = handler.handle(test_case['context'].copy())
                need_user_input = result_context.get('need_user_input', False)
                print(f"处理结果: 槽位完整，无需用户输入")
            except SlotHandlerInterrupt as e:
                print(f"处理结果: 需要用户输入")
                print(f"中断上下文中的缺失槽位: {e.context.get('missing_slots', [])}")
                print(f"中断上下文中的提示消息: {e.context.get('prompt_message', '')}")

        except Exception as e:
            print(f"处理出错: {e}")

    # 测试保存上下文功能
    print("\n" + "=" * 40)
    print("测试保存上下文功能")
    print("=" * 40)

    test_context = {
        'user_id': 'history_test_user',
        'session_id': 'history_test_session',
        'intent': 'order_food',
        'slots': {
            "场景": "家庭聚餐",
            "人数": "5人"
        },
        'location': '北京',
        'input_text': '我想点菜，5个人吃',
        'is_order': True
    }

    try:
        cache_key = f"context_history:{test_context['user_id']}:{test_context['session_id']}"

        # 保存上下文
        handler._save_context_to_history(
            test_context['user_id'],
            test_context['session_id'],
            test_context
        )
        print("上下文保存成功")

        # 验证保存的内容
        saved_context = handler.cache.get(cache_key)
        if saved_context:
            print("保存的上下文字段:")
            for key, value in saved_context.items():
                print(f"  {key}: {value}")
        else:
            print("未能从缓存中获取保存的上下文")

    except Exception as e:
        print(f"保存上下文时出错: {e}")

    # 测试提示消息生成
    print("\n" + "=" * 40)
    print("测试提示消息生成")
    print("=" * 40)

    message_tests = [
        {
            "name": "点餐意图提示",
            "missing_slots": ["菜系", "口味"],
            "intent": "order_food"
        },
        {
            "name": "游戏推荐意图提示",
            "missing_slots": ["场景", "人数", "游戏"],
            "intent": "recommend_game"
        },
        {
            "name": "营养查询意图提示",
            "missing_slots": ["忌口", "过敏原"],
            "intent": "query_nutrition"
        }
    ]

    for test in message_tests:
        print(f"\n{test['name']}:")
        message = handler._generate_prompt_message(test['missing_slots'], test['intent'])
        print(message)


if __name__ == "__main__":
    test_context_validation_and_history_handler()
