"""
prompt.py - 优化后的 PromptBuilder 实现
"""

import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入模块（假设这些模块和配置已存在）
try:
    from slot.slot_extractor import extract_slots
    from mcp.weather_client import get_weather_by_location
    from prompt_builder.config import (
        GAME_RECOMMENDATION_RULES,
        GAME_ENVIRONMENT_MAP,
        ORDER_KEYWORDS,
        INTENT_TO_TEMPLATE_MAP
    )
    from collector.templates.template import PromptTemplateLoader
    from intent.nlu_classifier import IntentClassifier
    from intent.classifier import IntentPredictor
    from database.DB import get_user_order_history, get_user_played_games
except ImportError as e:
    logger.error(f"导入模块失败: {e}")
    raise


class PromptConfig:
    """
    配置管理类

    提供默认配置参数，支持自定义配置
    """

    # 缓存配置
    TOKENIZE_CACHE_SIZE = 1000
    TEMPLATE_CACHE_SIZE = 128

    # 模板选择权重
    TEMPLATE_WEIGHTS = {
        "pre_meal_game_recommendation": 10,
        "healthy_diet_recommendation": 5,
        "weight_loss_meal_recommendation": 8,
        "fitness_meal_recommendation": 8,
        "intermittent_fasting_or_low_sugar_meal": 8,
        "vegetarian_meal_recommendation": 7,
        "cold_weather_meal_recommendation": 6,
        "summer_refreshing_meal_recommendation": 6,
        "festival_special_meal_recommendation": 9,
        "child_or_elderly_health_meal": 7,
        "enhanced_basic_with_all": 1
    }

    def __init__(self, **kwargs):
        """初始化配置

        Args:
            **kwargs: 自定义配置参数
        """
        # 设置默认值或使用传入的值
        self.max_length = kwargs.get("max_length", 512)
        self.default_language = kwargs.get("default_language", 'zh-CN')
        self.use_ml_intent = kwargs.get("use_ml_intent", False)


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
        self.config = config or PromptConfig()
        self.max_length = getattr(self.config, "max_length", 512)
        self.default_language = getattr(self.config, "default_language", 'zh-CN')

        # 加载模板管理器
        try:
            self.template_manager = self._load_template_manager()
        except Exception as e:
            logger.error(f"初始化模板管理器失败: {e}")
            raise

        # 初始化意图分类器
        self.intent_classifier = self._initialize_intent_classifier(intent_classifier)

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

    def build_prompt(self, input_text, user_id=None, location="北京", is_order_placed=False, **kwargs):
        """构建标准提示词

        Args:
            input_text: 用户输入文本
            user_id: 用户ID（用于获取历史数据）
            location: 当前城市（用于天气和地方菜系）
            is_order_placed: 是否已下单（外部传入）
            **kwargs: 其他参数（如 template_name, language 等）

        Returns:
            str: 构建好的提示词
        """
        try:
            # 1. 归一化输入
            cleaned_text = self._clean_input(input_text)

            # 2. 获取分词器
            from dict.ltp_tokenizer import get_tokenizer
            tokenizer = get_tokenizer()

            # 3. 单次分词：避免在槽位提取和意图识别中重复调用
            tokenized_text = tokenizer.tokenize(cleaned_text.lower())

            # 4. 提取槽位信息（传递已有的分词结果以避免重复计算）
            slots = self._extract_slots(cleaned_text, tokenizer, tokenized_text)

            # 5. 自动检测是否已下单（使用已有的分词结果）
            is_order_placed = is_order_placed or self._detect_order_intent(tokenized_text)

            # 6. 获取天气信息
            weather_info = self._get_weather(location)

            # 7. 获取用户数据（可选）
            order_history, played_games = self._get_user_data(user_id)

            # 8. 补全缺失槽位
            self._complete_missing_slots(slots, played_games)

            # 9 & 11. 生成游戏推荐 & 选择模板（合并步骤）
            intent = self.intent_classifier.classify(input_text)
            if is_order_placed:
               intent = self._generate_game_recommendation(slots)
            template_name = self._select_template(kwargs, intent)  # 直接使用原始输入文本

            # 10. 构建上下文（使用预定义变量）
            context_dict = self._build_context(
                slots=slots,
                location=location,
                weather_info=weather_info,
                order_history=order_history,
                played_games=played_games,
                user_request=input_text
            )

            language = kwargs.get("language", self.default_language)

            # 12. 渲染模板
            rendered_prompt = self.template_manager.get_template(template_name, lang=language, **context_dict)

            # 13. 清洗最终结果
            return self.remove_empty_lines(rendered_prompt)

        except Exception as e:
            logger.error(f"构建提示词时发生错误: {e}", exc_info=True)
            raise


    def _extract_slots(self, text, tokenizer, tokenized_text=None):
        """提取槽位并合并多次提取的结果

        Args:
            text: 输入文本
            tokenizer: 分词器实例
            tokenized_text: 已分词文本（可选）

        Returns:
            dict: 提取并合并后的槽位字典
        """
        if tokenized_text is None:
            tokenized_text = tokenizer.tokenize(text)

        # 第一次提取：原始文本匹配
        slots = extract_slots(text)

        # 第二次提取：分词后文本匹配
        additional_slots = extract_slots(tokenized_text)

        # 合并槽位
        merged_slots = {}
        for k in set(slots.keys()) | set(additional_slots.keys()):
            v1 = slots.get(k)
            v2 = additional_slots.get(k)

            if k in ["忌口", "过敏原"]:
                merged_slots[k] = list(set((v1 or []) + (v2 or [])))
            elif v1 or v2:
                merged_slots[k] = v1 or v2

        return merged_slots

    def _detect_order_intent(self, tokenized_text):
        """检测用户是否有下单意图（使用已分词文本）

        Args:
            tokenized_text: 已分词的文本

        Returns:
            bool: 是否有下单意图
        """
        if not tokenized_text:
            return False

        return any(keyword in tokenized_text for keyword in ORDER_KEYWORDS)

    def _get_weather(self, location):
        """获取天气信息

        Args:
            location: 城市名称

        Returns:
            dict: 天气信息
        """
        try:
            return get_weather_by_location(location) or {}
        except Exception as e:
            logger.warning(f"获取天气信息失败: {e}")
            return {}

    def _get_user_data(self, user_id):
        """获取用户数据

        Args:
            user_id: 用户ID

        Returns:
            tuple: (订单历史, 玩过的游戏)
        """
        if not user_id:
            return [], []

        try:
            return get_user_order_history(user_id), get_user_played_games(user_id)
        except Exception as e:
            logger.warning(f"获取用户数据失败: {e}")
            return [], []

    def _complete_missing_slots(self, slots, played_games):
        """补全缺失槽位

        Args:
            slots: 提取的槽位字典
            played_games: 玩过的游戏列表
        """
        if "人数" not in slots:
            if "场景" in slots and "朋友聚会" in slots.get("场景", ""):
                slots["人数"] = len(played_games) + 1 if played_games else 4

    def _generate_game_recommendation(self, slots):
        """基于场景和环境生成游戏推荐

        Args:
            slots: 槽位字典

        Returns:
            list: 推荐的游戏列表
        """
        scene = slots.get("场景")
        environment = slots.get("就餐环境")

        recommendations = []

        # 基于场景推荐游戏
        if scene in GAME_RECOMMENDATION_RULES:
            recommendations.extend(GAME_RECOMMENDATION_RULES[scene])

        # 基于就餐环境过滤
        if environment and environment in GAME_ENVIRONMENT_MAP:
            env_filtered = set(recommendations) & set(GAME_ENVIRONMENT_MAP[environment])
            recommendations = list(env_filtered)

        return recommendations

    def _build_context(self, **kwargs):
        """构建模板上下文字典

        Args:
            **kwargs: 上下文参数

        Returns:
            dict: 包含模板所需变量的上下文字典
        """
        slots = kwargs.get("slots", {})
        location = kwargs.get("location", "北京")
        weather_info = kwargs.get("weather_info", {})
        order_history = kwargs.get("order_history", [])
        played_games = kwargs.get("played_games", [])
        user_request = kwargs.get("user_request", "")

        try:
            context = {
                "user_request": user_request,
                "city": location,

                # 用户画像分析字段
                "scene": slots.get("场景"),
                "people_count": slots.get("人数"),
                "cuisine": slots.get("菜系"),
                "taste": slots.get("口味"),
                "drink": slots.get("饮品"),
                "environment": slots.get("就餐环境"),
                "meal_type": slots.get("就餐形式"),

                # 健康与饮食限制字段
                "health_preference": slots.get("健康偏好"),
                "dietary_restriction": slots.get("忌口"),
                "allergy_avoidance": slots.get("过敏原"),

                # 外部条件影响字段
                "weather": slots.get("天气状态") or weather_info.get("天气"),
                "special_event": slots.get("特殊节日"),

                # 历史数据
                "conversation_history": "",  # 如果有对话历史可传入
                "order_history": "\n".join(order_history) if order_history else "无",
                "is_order_placed": slots.get("已下单", False),

                # 地方特色菜品
                "local_dishes": self._get_local_dishes(location, slots.get("菜系")),

                # 所有其他槽位作为备用
                **{k: v for k, v in slots.items() if k not in locals()}
            }

            return context

        except Exception as e:
            logger.error(f"映射槽位到模板变量时发生错误: {e}", exc_info=True)
            raise

    def _select_template(self, kwargs, intent):
        """根据意图选择模板

        Args:
            kwargs: 其他参数
            user_request: 用户请求

        Returns:
            str: 选择的模板名称
        """
        template_name = kwargs.get("template_name")
        if template_name:
            return template_name

        try:

            selected = INTENT_TO_TEMPLATE_MAP.get(intent, "enhanced_basic_with_all")
            logger.info(f"根据意图 '{intent}' 选择了模板 '{selected}'")
            return selected
        except Exception as e:
            logger.warning(f"意图分类失败，使用默认模板: {e}")
            return "enhanced_basic_with_all"

    def _clean_input(self, text):
        """清洗用户输入文本

        Args:
            text: 原始输入字符串

        Returns:
            str: 清洗后的字符串
        """
        if not text:
            return ""

        # 去除首尾空白字符
        text = text.strip()

        # 限制最大长度（防止恶意或异常输入）
        if len(text) > self.max_length:
            logger.info(f"输入超过最大长度限制 {self.max_length}，已截断")
            return text[:self.max_length]

        return text

    def remove_empty_lines(self, text):
        """去除文本中的空行（包括只含空白字符的行）

        Args:
            text: 输入文本

        Returns:
            str: 清洗后的文本
        """
        lines = text.splitlines()
        cleaned_lines = [line.rstrip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)

    def _get_local_dishes(self, location, cuisine=None):
        """获取当前城市的特色菜品

        Args:
            location: 城市名称
            cuisine: 菜系类型（可选）

        Returns:
            str: 特色菜品字符串
        """
        city_dishes_map = {
            "北京": ["烤鸭", "炸酱面", "涮羊肉"],
            "成都": ["火锅", "夫妻肺片", "担担面"],
            "广州": ["早茶", "烧味", "白切鸡"],
            "上海": ["小笼包", "红烧肉", "腌笃鲜"],
            "杭州": ["西湖醋鱼", "龙井虾仁", "东坡肉"]
        }

        dishes = city_dishes_map.get(location, ["地方特色菜"])

        if cuisine:
            cuisine_based_map = {
                "川菜": ["麻辣香锅", "水煮鱼", "麻婆豆腐"],
                "粤菜": ["烧味", "白切鸡", "早茶"],
                "本帮菜": ["红烧肉", "腌笃鲜", "油爆虾"],
                "日料": ["寿司", "刺身", "味噌汤"]
            }
            dishes = cuisine_based_map.get(cuisine, dishes)

        return ", ".join(dishes)

if __name__ == '__main__':
    property = PromptBuilder()
    prompt = property.build_prompt(input_text="我要吃辣的牛排")
    print(prompt)