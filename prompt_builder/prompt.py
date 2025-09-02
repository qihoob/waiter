# E:\work\waiter\prompt_builder\prompt.py
import logging
import sys
import argparse
import os
import gc

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入模块（假设这些模块和配置已存在）
try:
    from prompt_builder.config import (
        GAME_RECOMMENDATION_RULES,
        GAME_ENVIRONMENT_MAP,
        ORDER_KEYWORDS,
        INTENT_TO_TEMPLATE_MAP
    )
    from slot.SlotHandler import SlotHandler, SlotHandlerInterrupt
    from slot.TextCleaningSlotHandler import TextCleaningSlotHandler
    from slot.TokenizationSlotHandler import TokenizationSlotHandler
    from slot.BaseSlotExtractionHandler import BaseSlotExtractionHandler
    from slot.OrderDetectionSlotHandler import OrderDetectionSlotHandler
    from slot.WeatherSlotHandler import WeatherSlotHandler
    from slot.UserDataSlotHandler import UserDataSlotHandler
    from slot.MissingSlotCompletionHandler import MissingSlotCompletionHandler
    from slot.SceneSlotHandler import SceneSlotHandler
    from slot.PeopleCountSlotHandler import PeopleCountSlotHandler
    from slot.CuisineFlavorHandler import CuisineFlavorHandler
    from slot.TasteSlotHandler import TasteSlotHandler
    from slot.HealthPreferenceSlotHandler import HealthPreferenceSlotHandler
    from slot.GameSlotHandler import GameSlotHandler
    from slot.TemplateSelectionSlotHandler import TemplateSelectionSlotHandler
    from slot.ContextBuildingSlotHandler import ContextBuildingSlotHandler
    from slot.TemplateRenderingSlotHandler import TemplateRenderingSlotHandler
    from slot.ContextHistoryRetrievalHandler import ContextHistoryRetrievalHandler
    from slot.ContextHistorySaveHandler import ContextHistorySaveHandler
    from slot.SinglePersonSceneHandler import SinglePersonSceneHandler

    # 新增的SlotHandler处理器
    from slot.AllergenSlotHandler import AllergenSlotHandler
    from slot.DietaryRestrictionSlotHandler import DietaryRestrictionSlotHandler
    from slot.DishBasedCuisineClassifier import DishBasedCuisineClassifier
    from slot.DrinkSlotHandler import DrinkSlotHandler
    from slot.FestivalSlotHandler import FestivalSlotHandler
    from slot.LocationSlotHandler import LocationSlotHandler
    from slot.SlotValidationHandler import SlotValidationHandler
    from slot.SinglePersonSceneHandler import SinglePersonSceneHandler  # 新增一个人用餐场景处理器

    from collector.templates.template import PromptTemplateLoader
    from intent.nlu_classifier import IntentClassifier
    from intent.classifier import IntentPredictor
    from database.DB import get_user_order_history, get_user_played_games
    from mcp.weather_client import get_weather_by_location

    # 导入全局变量管理模块
    from slot.global_vars import (
        initialize_global_services,
        get_global_config,
        get_global_template_manager,
        get_global_intent_classifier,
        is_global_initialized
    )
    
    # 导入上下文管理器
    from slot.ContextManager import get_context_manager
except ImportError as e:
    logger.error(f"导入模块失败: {e}")
    raise

# 初始化全局服务
default_config = {
    "max_length": 512,
    "default_language": 'zh-CN',
    "use_ml_intent": False
}
initialize_global_services(config=default_config)

class PromptBuilder:
    """
    构建提示词的核心类

    特性：
    - 支持意图识别
    - 支持槽位提取
    - 支持多模板渲染
    - 支持自定义词典
    - 支持上下文感知
    """

    def __init__(self, config=None, intent_classifier=None):
        """初始化PromptBuilder

        Args:
            config: 可选，自定义配置
            intent_classifier: 可选，自定义意图分类器实例
        """
        # 使用全局服务
        self.config = get_global_config()
        self.template_manager = get_global_template_manager()
        self.intent_classifier = get_global_intent_classifier()
        self.max_length = getattr(self.config, "max_length", 512)
        self.default_language = getattr(self.config, "default_language", 'zh-CN')

    def build_prompt(self, input_text, user_id=None, location="北京", is_order=False, intent=None, **kwargs):
        """构建提示词

        Args:
            input_text: 用户输入文本
            user_id: 用户ID
            location: 位置信息
            is_order: 是否已下单
            intent: 意图
            **kwargs: 其他参数

        Returns:
            str: 构建好的提示词
        """
        try:
            # 获取全局上下文管理器
            context_manager = get_context_manager()
            
            # 更新上下文管理器中的基础信息
            context_manager.update_context({
                'input': {
                    'text': input_text
                },
                'user': {
                    'id': user_id
                },
                'environment': {
                    'location': location
                },
                'recognition': {
                    'is_order': is_order,
                    'intent': intent
                }
            })
            
            # 获取上下文
            context = context_manager.get_context()
            # 构建完整的槽位处理责任链
            slot_handler_chain = self._build_complete_slot_chain()

            # 处理请求并获取结果
            try:
                result = slot_handler_chain.handle(context)
                return result.get("result", "未能生成提示词")
            except SlotHandlerInterrupt as e:
                # 处理链被中断，返回中断时的上下文
                logger.info("处理链被中断，等待用户输入")
                return self._handle_chain_interruption(context)

        except Exception as e:
            logger.error(f"构建提示词时发生错误: {e}", exc_info=True)
            return f"提示词构建失败: {str(e)}"

    def _build_complete_slot_chain(self) -> SlotHandler:
        """
        构建完整的槽位处理责任链，包含所有可用的SlotHandler处理器

        Returns:
            SlotHandler: 构建好的处理链起始节点
        """
        # 第一阶段：文本预处理
        text_cleaning_chain = TextCleaningSlotHandler()  # 文本清洗
        chain = text_cleaning_chain.set_next(TokenizationSlotHandler())  # 文本分词

        # 第二阶段：基础信息提取
        chain = chain.set_next(BaseSlotExtractionHandler())  # 基础槽位提取
        chain = chain.set_next(OrderDetectionSlotHandler())  # 订单检测
        chain = chain.set_next(LocationSlotHandler())  # 位置信息提取
        chain = chain.set_next(WeatherSlotHandler())  # 天气信息提取
        chain = chain.set_next(UserDataSlotHandler())  # 用户数据提取

        # 第三阶段：场景和人数信息提取
        chain = chain.set_next(SceneSlotHandler())  # 场景信息提取
        chain = chain.set_next(SinglePersonSceneHandler())  # 一个人用餐场景处理
        chain = chain.set_next(PeopleCountSlotHandler())  # 人数信息提取

        # 第四阶段：餐饮相关信息提取
        chain = chain.set_next(DishBasedCuisineClassifier())  # 基于菜品的菜系分类
        chain = chain.set_next(CuisineFlavorHandler())  # 菜系信息提取
        chain = chain.set_next(TasteSlotHandler())  # 口味信息提取
        chain = chain.set_next(HealthPreferenceSlotHandler())  # 健康偏好提取
        chain = chain.set_next(DietaryRestrictionSlotHandler())  # 忌口信息提取
        chain = chain.set_next(AllergenSlotHandler())  # 过敏原信息提取
        chain = chain.set_next(DrinkSlotHandler())  # 饮品信息提取

        # 第五阶段：其他信息提取
        chain = chain.set_next(FestivalSlotHandler())  # 节日信息提取
        chain = chain.set_next(GameSlotHandler())  # 游戏推荐信息提取

        # 第六阶段：上下文管理和槽位补全
        chain = chain.set_next(ContextHistoryRetrievalHandler())  # 上下文历史检索
        #chain = chain.set_next(MissingSlotCompletionHandler())  # 缺失槽位补全
        chain = chain.set_next(SlotValidationHandler())  # 槽位验证
        chain = chain.set_next(ContextHistorySaveHandler())  # 上下文历史保存

        # 第七阶段：模板处理
        chain = chain.set_next(TemplateSelectionSlotHandler())  # 模板选择
        chain = chain.set_next(ContextBuildingSlotHandler())  # 上下文构建
        chain = chain.set_next(TemplateRenderingSlotHandler())  # 模板渲染

        # 返回链的起始节点
        return text_cleaning_chain

    def _handle_chain_interruption(self, context: dict) -> str:
        """
        处理槽位链中断情况

        Args:
            context: 中断时的上下文

        Returns:
            str: 适当的响应信息
        """
        # 检查是否有缺失槽位需要用户补充
        missing_slots = context.get('missing_slots', [])
        if missing_slots:
            prompt_msg = context.get('prompt_message')
            if prompt_msg:
                return prompt_msg

        # 默认响应
        return "请提供更多信息以便更好地为您服务"

    def _load_template_manager(self):
        """加载模板管理器"""
        return PromptTemplateLoader()

    def _initialize_intent_classifier(self, intent_classifier):
        """初始化意图分类器"""
        if intent_classifier:
            return intent_classifier

        use_ml_intent = getattr(self.config, "use_ml_intent", False)
        if use_ml_intent:
            try:
                ml_classifier = IntentPredictor()
                if not getattr(ml_classifier, "is_trained", False):
                    logger.info("开始训练意图分类模型")
                    ml_classifier.train()
                return ml_classifier
            except Exception as e:
                logger.warning(f"加载机器学习意图分类器失败，回退到规则分类器: {e}")

        return IntentClassifier()

class PromptCommandLineInterface:
    """命令行交互界面类"""

    def __init__(self):
        self.prompt_builder = PromptBuilder()
        self.user_id = "cli_user"
        self.location = "北京"

    def start_interactive_mode(self):
        """启动交互模式"""
        print("=" * 60)
        print("🍽️  智能提示词构建器 - 完整版交互模式")
        print("=" * 60)
        print("📝 输入您的请求，系统将为您构建相应的提示词")
        print("💡 示例:")
        print("   • 我想点一份牛排")
        print("   • 4人聚餐，来点香辣菜")
        print("   • 推荐一些适合夏天的清爽菜品")
        print("   • 有什么适合减肥的餐品")
        print("   • 我想吃清淡一点的白切鸡")
        print("   • 三个人吃粤菜有什么推荐？")
        print("   • 我对花生过敏，想要低脂的食物")
        print("   • 情侣约会想玩游戏，推荐一下")
        print("-" * 60)
        print("⌨️  命令:")
        print("   • 'help' 或 '帮助' - 显示帮助信息")
        print("   • 'quit' 或 'exit' 或 '退出' - 退出程序")
        print("   • 'clear' 或 'cls' - 清屏")
        print("=" * 60)

        while True:
            try:
                user_input = input("\n💬 请输入您的请求: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("👋 感谢使用，再见！")
                    break
                elif user_input.lower() in ['help', '帮助']:
                    self._show_help()
                    continue
                elif user_input.lower() in ['clear', 'cls']:
                    self._clear_screen()
                    continue
                elif not user_input:
                    continue

                # 构建提示词
                result = self.prompt_builder.build_prompt(
                    input_text=user_input,
                    user_id=self.user_id,
                    location=self.location
                )

                print("\n🤖 生成的提示词:")
                print("─" * 40)
                print(result)
                print("─" * 40)

            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断，再见！")
                break
            except Exception as e:
                print(f"\n❌ 处理请求时发生错误: {e}")
                logger.error(f"交互模式错误: {e}", exc_info=True)

    def _show_help(self):
        """显示帮助信息"""
        help_text = """
📖 可用命令:
  help      - 显示此帮助信息
  quit/exit - 退出程序
  clear/cls - 清屏

🍽️ 使用说明:
  直接输入您的自然语言请求，系统支持多种信息识别:
  
  🍜 餐饮相关:
    - "我想点一份牛排"
    - "4人聚餐，来点香辣菜"
    - "推荐一些适合夏天的清爽菜品"
    - "有什么适合减肥的餐品"
    - "我想吃清淡一点的白切鸡"
    - "三个人吃粤菜有什么推荐？"
    - "我想要一杯可乐和珍珠奶茶"
    
  🚫 健康相关:
    - "我对花生过敏"
    - "不吃辣，要清淡的"
    - "我在减肥，想要低脂的食物"
    
  🎮 娱乐相关:
    - "朋友聚会想玩游戏"
    - "情人节推荐一些浪漫的游戏"
    
  🏠 其他场景:
    - "今天天气怎么样，推荐点什么？"
    - "圣诞节想和家人一起吃饭"

🧠 系统特性:
  - 自动识别菜系（川菜、粤菜、湘菜等）
  - 识别特色菜品和口味偏好
  - 理解人数、场景等用餐信息
  - 根据历史上下文优化推荐
  - 支持健康偏好、忌口和过敏原需求
  - 识别节日和特殊场景
  - 支持游戏推荐
        """
        print(help_text)

    def _clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def run_single_prompt(self, input_text, user_id=None, location=None):
        """运行单次提示词生成"""
        try:
            result = self.prompt_builder.build_prompt(
                input_text=input_text,
                user_id=user_id or self.user_id,
                location=location or self.location
            )
            return result
        except Exception as e:
            logger.error(f"单次提示词生成错误: {e}", exc_info=True)
            return f"生成提示词时发生错误: {e}"

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能提示词构建器 - 完整版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                           # 启动交互模式
  %(prog)s -I                        # 启动交互模式（同上）
  %(prog)s -i "我想吃清淡的白切鸡"   # 单次执行模式
  %(prog)s --input "推荐粤菜" --user-id user123
        """
    )
    parser.add_argument('--input', '-i', type=str, help='输入文本')
    parser.add_argument('--user-id', type=str, default='cli_user', help='用户ID')
    parser.add_argument('--location', type=str, default='北京', help='位置信息')
    parser.add_argument('--interactive', '-I', action='store_true', help='启动交互模式')

    try:
        args = parser.parse_args()

        # 创建CLI实例
        cli = PromptCommandLineInterface()

        if args.interactive:
            # 启动交互模式
            cli.start_interactive_mode()
        elif args.input:
            # 单次执行模式
            result = cli.run_single_prompt(args.input, args.user_id, args.location)
            print("🤖 生成的提示词:")
            print(result)
        else:
            # 默认启动交互模式
            cli.start_interactive_mode()
    except Exception as e:
        logger.error(f"程序执行出错: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f"程序启动失败: {e}", exc_info=True)
        sys.exit(1)
