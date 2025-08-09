# E:\work\waiter\prompt_builder\prompt.py
"""
prompt.py - 优化后的 PromptBuilder 实现
"""

import logging
import sys
import argparse
import os

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入模块（假设这些模块和配置已存在）
try:
    from slot.slot_extractor import extract_slots
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
    from slot.CuisineSlotHandler import CuisineSlotHandler
    from slot.TasteSlotHandler import TasteSlotHandler
    from slot.HealthPreferenceSlotHandler import HealthPreferenceSlotHandler
    from slot.GameRecommendationSlotHandler import GameRecommendationSlotHandler
    from slot.TemplateSelectionSlotHandler import TemplateSelectionSlotHandler
    from slot.ContextBuildingSlotHandler import ContextBuildingSlotHandler
    from slot.TemplateRenderingSlotHandler import TemplateRenderingSlotHandler
    from slot.ContextHistoryRetrievalHandler import ContextHistoryRetrievalHandler
    from slot.ContextHistorySaveHandler import ContextHistorySaveHandler

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
except ImportError as e:
    logger.error(f"导入模块失败: {e}")
    raise

# 初始化全局服务（在模块导入时自动初始化）
if not is_global_initialized():
    # 使用默认配置初始化全局服务
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

    def build_prompt(self, input_text, user_id=None, location="北京", is_order_placed=False, intent=None, **kwargs):
        """构建提示词

        Args:
            input_text: 用户输入文本
            user_id: 用户ID
            location: 位置信息
            is_order_placed: 是否已下单
            intent: 意图
            **kwargs: 其他参数

        Returns:
            str: 构建好的提示词
        """
        try:
            # 构建初始上下文
            context = {
                'input_text': input_text,
                'user_id': user_id,
                'location': location,
                'is_order_placed': is_order_placed,
                'intent': intent,
                'kwargs': kwargs
            }

            # 构建槽位处理责任链
            slot_handler_chain = TextCleaningSlotHandler()
            slot_handler_chain.set_next(TokenizationSlotHandler()) \
                .set_next(BaseSlotExtractionHandler()) \
                .set_next(OrderDetectionSlotHandler()) \
                .set_next(WeatherSlotHandler()) \
                .set_next(UserDataSlotHandler()) \
                .set_next(SceneSlotHandler()) \
                .set_next(PeopleCountSlotHandler()) \
                .set_next(CuisineSlotHandler()) \
                .set_next(TasteSlotHandler()) \
                .set_next(HealthPreferenceSlotHandler()) \
                .set_next(ContextHistoryRetrievalHandler())\
                .set_next(ContextHistorySaveHandler()) \
                .set_next(TemplateSelectionSlotHandler()) \
                .set_next(ContextBuildingSlotHandler()) \
                .set_next(TemplateRenderingSlotHandler())

            # 处理请求并获取结果
            try:
                result = slot_handler_chain.handle(context)
                return result["result"]
            except SlotHandlerInterrupt as e:
            # 处理链被中断，返回中断时的上下文
                logger.info("处理链被中断，等待用户输入")
                return e.result
            return result_context['result']

        except Exception as e:
            logger.error(f"构建提示词时发生错误: {e}", exc_info=True)
            raise

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
        print("=" * 50)
        print("智能提示词构建器 - 交互模式")
        print("=" * 50)
        print("输入您的请求，系统将为您构建相应的提示词")
        print("输入 'quit' 或 'exit' 退出程序")
        print("输入 'help' 查看帮助信息")
        print("-" * 50)

        while True:
            try:
                user_input = input("\n请输入您的请求: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("感谢使用，再见！")
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

                print("\n生成的提示词:")
                print("-" * 30)
                print(result)
                print("-" * 30)

            except KeyboardInterrupt:
                print("\n\n程序被用户中断，再见！")
                break
            except Exception as e:
                print(f"\n处理请求时发生错误: {e}")
                logger.error(f"交互模式错误: {e}", exc_info=True)

    def _show_help(self):
        """显示帮助信息"""
        help_text = """
可用命令:
  help      - 显示此帮助信息
  quit/exit - 退出程序
  clear/cls - 清屏
  
使用说明:
  直接输入您的自然语言请求，例如:
  - "我想点一份牛排"
  - "4人聚餐，来点香辣菜"
  - "推荐一些适合夏天的清爽菜品"
  - "有什么适合减肥的餐品"
  
系统将根据您的请求生成相应的提示词。
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
    parser = argparse.ArgumentParser(description="智能提示词构建器")
    parser.add_argument('--input', '-i', type=str, help='输入文本')
    parser.add_argument('--user-id', type=str, default='cli_user', help='用户ID')
    parser.add_argument('--location', type=str, default='北京', help='位置信息')
    parser.add_argument('--interactive', '-I', action='store_true', help='启动交互模式')

    args = parser.parse_args()

    # 创建CLI实例
    cli = PromptCommandLineInterface()

    if args.interactive:
        # 启动交互模式
        cli.start_interactive_mode()
    elif args.input:
        # 单次执行模式
        result = cli.run_single_prompt(args.input, args.user_id, args.location)
        print(result)
    else:
        # 默认启动交互模式
        cli.start_interactive_mode()


if __name__ == '__main__':
    main()
