# prompt.py - 完整的 PromptBuilder 实现

import os
import jieba
from collector.prompt_builder.slot_extractor import extract_slots
from collector.prompt_builder.nlu_service import IntentClassifier
from database.DB  import get_user_order_history, get_user_played_games
from mcp.weather_client import get_weather_by_location
from collector.prompt_builder.config import (
    GAME_RECOMMENDATION_RULES,
    GAME_ENVIRONMENT_MAP,
    ORDER_KEYWORDS,
    INTENT_TO_TEMPLATE_MAP
)
from collector.prompt_builder.template import PromptTemplateLoader


class PromptBuilder:
    def __init__(self, max_length=512, dict_path="E:\\work\\waiter\\collector\\custom_dict.txt"):
        self.max_length = max_length
        self.default_language = 'zh-CN'
        self.dict_path = dict_path
        template_file_path = "E:\\work\\waiter\\collector\\templates\\prompt_templates.yaml"
        self.template_manager = PromptTemplateLoader(template_file_path)
        self.intent_classifier = IntentClassifier()

        # 加载自定义词典
        self._load_custom_dict()

    def _load_custom_dict(self):
        """加载自定义词典"""
        if os.path.exists(self.dict_path):
            try:
                jieba.load_userdict(self.dict_path)
                print(f"[INFO] 自定义词典 {self.dict_path} 加载成功")
            except Exception as e:
                print(f"[ERROR] 加载自定义词典失败: {e}")
        else:
            print(f"[WARNING] 自定义词典文件不存在: {self.dict_path}")

    def reload_custom_dict(self):
        """重新加载自定义词典（热加载）"""
        jieba.del_word(" ")  # 清除缓存词汇（可选）
        self._load_custom_dict()
        print("[INFO] 自定义词典已重新加载")

    def _clean_input(self, text):
        """
        清洗用户输入文本
        :param text: 原始输入字符串
        :return: 清洗后的字符串
        """
        if not text:
            return ""

        # 去除首尾空白字符
        text = text.strip()

        # 限制最大长度（防止恶意或异常输入）
        if len(text) > self.max_length:
            text = text[:self.max_length]

        return text

    def _chinese_tokenize(self, text):
        """
        对中文文本进行分词，使用自定义词典提升识别准确率
        :param text: 输入文本
        :return: 分词后的字符串
        """
        if not text:
            return ""

        tokens = jieba.cut(text, cut_all=False)
        return " ".join(tokens)

    def detect_order_intent(self, text):
        """
        检测用户是否有下单意图
        """
        for keyword in ORDER_KEYWORDS:
            if keyword in text:
                return True
        return False

    def build_prompt(self, input_text, user_id=None, location="北京", is_order_placed=False, **kwargs):
        """
        构建标准提示词
        :param input_text: 用户输入文本
        :param user_id: 用户ID（用于获取历史数据）
        :param location: 当前城市（用于天气和地方菜系）
        :param is_order_placed: 是否已下单（外部传入）
        :param kwargs: 其他参数（如 template_name, language 等）
        :return: 构建好的提示词
        """
        # 1. 归一化输入
        cleaned_text = self._clean_input(input_text)
        tokenized_text = self._chinese_tokenize(cleaned_text)

        # 2. 提取槽位
        slots = extract_slots(tokenized_text)

        # 3. 自动检测是否已下单
        is_order_placed = is_order_placed or self.detect_order_intent(tokenized_text)

        # 4. 获取天气信息
        weather_info = get_weather_by_location(location)

        # 5. 获取用户数据（可选）
        order_history = []
        played_games = []
        if user_id:
            order_history = get_user_order_history(user_id)
            played_games = get_user_played_games(user_id)

        # 6. 补全缺失槽位（如人数未提供时尝试推断）
        if "人数" not in slots and "朋友聚会" in slots.get("场景", ""):
            slots["人数"] = len(played_games) + 1 if played_games else 4  # 默认为4人

        # 7. 如果已下单，进入“餐前娱乐”推荐流程
        game_recommendation = []
        if is_order_placed:
            scene = slots.get("场景")
            environment = slots.get("就餐环境")

            # 基于场景推荐游戏
            if scene in GAME_RECOMMENDATION_RULES:
                game_recommendation.extend(GAME_RECOMMENDATION_RULES[scene])

            # 基于就餐环境过滤
            if environment in GAME_ENVIRONMENT_MAP:
                game_recommendation = list(set(game_recommendation) & set(GAME_ENVIRONMENT_MAP[environment]))

            # 合并到 slots
            slots["推荐游戏"] = ", ".join(game_recommendation) or "暂无推荐"

        # 8. 构建最终注入字典
        context_dict = self._map_slots_to_template_vars(
            slots=slots,
            weather_info=weather_info,
            order_history=order_history,
            played_games=played_games,
            game_recommendation=game_recommendation,
            user_request=input_text,
            location=location
        )

        # 9. 模板选择
        template_name = kwargs.get("template_name")
        if is_order_placed and not template_name:
            template_name = "pre_meal_game_recommendation"
        elif not template_name:
            intent = self.intent_classifier.classify(tokenized_text, slots)
            template_name = self.intent_choose_template(intent)

        language = kwargs.get("language", self.default_language)

        return self.template_manager.get_template(template_name, lang=language, **context_dict)


    def _choose_template(self, slots):
        """
        根据槽位内容智能选择最合适的模板，并返回最高分模板
        """
        template_scores = {
            "pre_meal_game_recommendation": 0,
            "healthy_diet_recommendation": 0,
            "weight_loss_meal_recommendation": 0,
            "fitness_meal_recommendation": 0,
            "intermittent_fasting_or_low_sugar_meal": 0,
            "vegetarian_meal_recommendation": 0,
            "cold_weather_meal_recommendation": 0,
            "summer_refreshing_meal_recommendation": 0,
            "festival_special_meal_recommendation": 0,
            "child_or_elderly_health_meal": 0,
            "enhanced_basic_with_all": 1  # 默认基础分
        }

        # 1. 游戏相关优先级最高
        if "游戏" in slots or "推荐游戏" in slots:
            template_scores["pre_meal_game_recommendation"] += 10

        # 2. 健康饮食类
        if "健康偏好" in slots:
            health_pref = slots["健康偏好"]
            if health_pref == "低脂":
                template_scores["weight_loss_meal_recommendation"] += 8
            elif health_pref == "高蛋白":
                template_scores["fitness_meal_recommendation"] += 8
            elif health_pref == "无糖":
                template_scores["intermittent_fasting_or_low_sugar_meal"] += 8
            elif health_pref == "清淡":
                template_scores["child_or_elderly_health_meal"] += 7
            template_scores["healthy_diet_recommendation"] += 5

        # 3. 素食者友好
        if "忌口" in slots and any(keyword in slots["忌口"] for keyword in ["素食", "不吃肉", "不吃荤"]):
            template_scores["vegetarian_meal_recommendation"] += 7

        # 4. 天气影响推荐
        if "天气状态" in slots:
            weather = slots["天气状态"]
            if weather in ["寒冷", "阴雨"]:
                template_scores["cold_weather_meal_recommendation"] += 6
            elif weather in ["炎热", "晴朗"]:
                template_scores["summer_refreshing_meal_recommendation"] += 6

        # 5. 节日或特殊场合
        if "特殊节日" in slots:
            template_scores["festival_special_meal_recommendation"] += 9

        # 6. 用户画像辅助判断
        if "忌口" in slots:
            if "忌海鲜" in slots["忌口"]:
                template_scores["healthy_diet_recommendation"] += 2
                template_scores["weight_loss_meal_recommendation"] += 1

        if "过敏原" in slots:
            if "花生" in slots["过敏原"]:
                template_scores["healthy_diet_recommendation"] += 2

        if "就餐形式" in slots:
            if "自助餐" in slots["就餐形式"]:
                template_scores["enhanced_basic_with_all"] += 3
            elif "围炉" in slots["就餐形式"]:
                template_scores["cold_weather_meal_recommendation"] += 2

        # 7. 返回得分最高的模板
        best_template = max(template_scores, key=template_scores.get)
        return best_template
    def intent_choose_template(self, intent):
        return INTENT_TO_TEMPLATE_MAP.get(intent, "enhanced_basic_with_all")


    def _map_slots_to_template_vars(self, slots, weather_info, order_history, played_games, game_recommendation, user_request, location):
        """
        将槽位字段映射为模板变量名，并补充额外信息
        :param slots: 提取的槽位字典
        :param weather_info: 天气信息
        :param order_history: 历史点单记录
        :param played_games: 玩过的游戏
        :param game_recommendation: 推荐的游戏列表
        :param user_request: 用户原始请求
        :param location: 当前城市（用于地方菜系）
        :return: 可供模板渲染使用的上下文字典
        """
        context = {
            # 基础信息
            "user_request": user_request,
            "city": location,

            # 槽位字段
            "scene": slots.get("场景"),
            "people_count": slots.get("人数"),
            "cuisine": slots.get("菜系"),
            "dietary_restriction": slots.get("忌口"),
            "allergy_avoidance": slots.get("过敏原"),
            "health_preference": slots.get("健康偏好"),
            "meal_type": slots.get("就餐形式"),
            "special_event": slots.get("特殊节日"),
            "environment": slots.get("就餐环境"),
            "weather": slots.get("天气状态") or weather_info.get("weather"),

            # 用户画像
            "order_history": "\n".join(order_history) if order_history else "无",
            "played_games": ", ".join(played_games) if played_games else "无",
            "game_recommendation": ", ".join(game_recommendation) if game_recommendation else "暂无推荐",

            # 外部数据补充
            "temperature": weather_info.get("temperature", 20),
            "is_order_placed": slots.get("已下单", False),

            # 地方特色菜补充字段（可选）
            "local_dishes": self._get_local_dishes(location, slots.get("菜系"))
        }

        return context

    def _get_local_dishes(self, location, cuisine=None):
        """
        获取当前城市的特色菜品
        :param location: 城市名称
        :param cuisine: 菜系类型（可选）
        :return: 特色菜品字符串
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