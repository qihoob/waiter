# E:\work\waiter\slot\DishBasedCuisineClassifier.py
from typing import Dict, Any, List
from slot.SlotHandler import SlotHandler
import re
from collections import defaultdict
from fuzzywuzzy import process
from prompt_builder.features_dict import cuisine_complete_info
import logging

logger = logging.getLogger(__name__)

class DishBasedCuisineClassifier(SlotHandler):
    """基于菜品的菜系分类器"""

    def __init__(self, next_handler=None, threshold=80):
        """
        初始化菜系分类器

        Args:
            next_handler: 下一个处理器
            threshold: 模糊匹配阈值
        """
        super().__init__(next_handler)
        self.threshold = threshold
        self.feature_map = self.build_feature_mapping(cuisine_complete_info)
        self.all_cuisine_names = list(cuisine_complete_info.keys())
        # 添加所有同义词到菜系名称列表中
        for details in cuisine_complete_info.values():
            self.all_cuisine_names.extend(details.get("同义词", []))

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            slots = context.get('slots', {})

            # 如果还没有识别到菜系，则进行菜系分类
            if '菜系' not in slots or not slots['菜系']:
                cuisine = self._classify_cuisine(context)
                if cuisine:
                    slots['菜系'] = cuisine
                    context['slots'] = slots

        except Exception as e:
            logger.warning(f"菜系分类过程中出错: {e}")

        return super().handle(context)

    def _classify_cuisine(self, context: Dict[str, Any]) -> str:
        """
        从上下文文本中分类菜系

        Args:
            context: 处理上下文

        Returns:
            str: 识别到的菜系（标准化后的名称）
        """
        # 按优先级获取文本
        texts = []

        # 优先级1: cleaned_text
        if context.get('cleaned_text'):
            texts.append(('cleaned_text', context['cleaned_text']))

        # 优先级2: input_text
        if context.get('input_text'):
            texts.append(('input_text', context['input_text']))

        # 优先级3: tokenized_text
        if context.get('tokenized_text'):
            texts.append(('tokenized_text', context['tokenized_text']))

        # 在每个文本中尝试识别菜系
        for text_type, text in texts:
            if not text:
                continue

            cuisine = self._extract_cuisine_from_text(text)
            if cuisine:
                logger.info(f"从{text_type}中识别到菜系: {cuisine}")
                return cuisine

        return None

    def _extract_cuisine_from_text(self, text: str) -> str:
        """
        从文本中提取菜系信息

        Args:
            text: 输入文本

        Returns:
            str: 识别到的菜系（标准化后的名称）
        """
        if not text:
            return None

        # 方法1: 通过菜品名称匹配菜系
        dish_cuisine = self._match_dish_to_cuisine(text)
        if dish_cuisine:
            return dish_cuisine

        # 方法2: 直接匹配菜系关键词
        direct_cuisine = self._match_cuisine_keywords(text)
        if direct_cuisine:
            return direct_cuisine

        # 方法3: 使用模糊匹配
        fuzzy_cuisine = self._fuzzy_match_cuisine(text)
        if fuzzy_cuisine:
            return fuzzy_cuisine

        return None

    def _match_dish_to_cuisine(self, text: str) -> str:
        """
        通过菜品名称匹配菜系

        Args:
            text: 输入文本

        Returns:
            str: 匹配到的菜系
        """
        # 使用特征映射表查找匹配的菜系
        for feature, cuisines in self.feature_map.items():
            if feature in text:
                # 如果找到匹配项，返回第一个匹配的菜系
                return cuisines[0]
        return None

    def _match_cuisine_keywords(self, text: str) -> str:
        """
        通过关键词直接匹配菜系

        Args:
            text: 输入文本

        Returns:
            str: 匹配到的菜系
        """
        for cuisine_name in self.all_cuisine_names:
            if cuisine_name in text:
                return self._standardize_cuisine_name(cuisine_name)
        return None

    def _fuzzy_match_cuisine(self, text: str) -> str:
        """
        使用模糊匹配识别菜系

        Args:
            text: 输入文本

        Returns:
            str: 匹配到的菜系
        """
        try:
            matched_cuisine, score = process.extractOne(text, self.all_cuisine_names)
            if score >= self.threshold:
                return self._standardize_cuisine_name(matched_cuisine)
        except Exception as e:
            logger.warning(f"菜系模糊匹配出错: {e}")

        return None

    def build_feature_mapping(self, cuisine_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        构建「特征 → 菜系」映射表，提取所有可用于反推的特征

        参数：
            cuisine_data: 完整的菜系信息字典（cuisine_complete_info）

        返回：
            feature_map: 字典，格式 {特征字符串: [菜系1, 菜系2, ...]}
        """
        feature_map = defaultdict(list)  # 特征到菜系的映射

        for cuisine_name, details in cuisine_data.items():
            # 1. 提取「菜系同义词」特征（如"四川菜"对应"川菜"）
            for synonym in details.get("同义词", []):
                feature = self._normalize_text(synonym)  # 标准化文本（小写、去标点）
                feature_map[feature].append(cuisine_name)

            # 2. 提取「特色菜名称及同义词」特征（如"麻婆豆腐"对应"川菜"）
            for dish in details.get("特色菜", []):
                # 特色菜名称
                dish_name = self._normalize_text(dish["名称"])
                feature_map[dish_name].append(cuisine_name)
                # 特色菜同义词
                for dish_syn in dish.get("同义词", []):
                    dish_syn_norm = self._normalize_text(dish_syn)
                    feature_map[dish_syn_norm].append(cuisine_name)

            # 3. 提取「家常菜名称及同义词」特征（如"回锅肉"对应"川菜"）
            for home_dish in details.get("家常菜", []):
                # 家常菜名称
                home_dish_name = self._normalize_text(home_dish["名称"])
                feature_map[home_dish_name].append(cuisine_name)
                # 家常菜同义词
                for home_syn in home_dish.get("同义词", []):
                    home_syn_norm = self._normalize_text(home_syn)
                    feature_map[home_syn_norm].append(cuisine_name)

            # 4. 提取「口味特点」相关特征
            taste = details.get("口味特点", {})
            # 核心口味（如"麻辣"对应"川菜"）
            for core_taste in taste.get("核心口味", []):
                core_taste_norm = self._normalize_text(core_taste)
                feature_map[core_taste_norm].append(cuisine_name)

            # 味型细分（如"鱼香味"对应"川菜"）
            for taste_detail in taste.get("味型细分", []):
                # 提取味型关键词（如从"鱼香味（酸甜辣平衡）"中提取"鱼香味"）
                match = re.match(r"^(.+?)(?:\(|\s)", taste_detail)
                if match:
                    taste_key = self._normalize_text(match.group(1))
                    feature_map[taste_key].append(cuisine_name)

            # 口味特点描述（如"百菜百味"对应"川菜"）
            desc_norm = self._normalize_text(taste.get("特点描述", ""))
            # 拆分描述为关键词（按标点/空格拆分）
            for desc_word in re.split(r"[，。, .\s]+", desc_norm):
                if len(desc_word) >= 2:  # 过滤太短的词（如"的""和"）
                    feature_map[desc_word].append(cuisine_name)

            # 5. 提取「菜系说明」中的关键词（如"浓油赤酱"对应"本帮菜"）
            intro_norm = self._normalize_text(details.get("说明", ""))
            for intro_word in re.split(r"[，。, .\s]+", intro_norm):
                if len(intro_word) >= 2:
                    feature_map[intro_word].append(cuisine_name)

        return feature_map

    def _normalize_text(self, text: str) -> str:
        """文本标准化：小写化、去除标点、空格"""
        if not text:
            return ""
        text = str(text).lower()  # 小写化
        text = re.sub(r"[^\w\s]", "", text)  # 去除标点
        text = text.strip()  # 去空格
        return text

    def _standardize_cuisine_name(self, name: str) -> str:
        """
        将菜系名称或同义词标准化为标准菜系名称

        Args:
            name: 菜系名称或同义词

        Returns:
            str: 标准菜系名称
        """
        normalized_name = self._normalize_text(name)
        # 在特征映射中查找对应的菜系
        for feature, cuisines in self.feature_map.items():
            if feature == normalized_name:
                return cuisines[0]  # 返回第一个匹配的菜系（标准名称）
        return name  # 如果找不到，返回原始名称

    def infer_cuisine(self, input_features: List[str], top_n: int = 3) -> List[Dict[str, Any]]:
        """
        根据输入特征反推菜系

        参数：
            input_features: 输入的特征列表（如["麻婆豆腐", "麻辣", "鱼香味"]）
            top_n: 返回匹配度最高的前N个菜系

        返回：
            排序后的菜系列表，格式 [{"cuisine": 菜系名, "count": 匹配次数}, ...]
        """
        # 标准化输入特征
        normalized_inputs = [self._normalize_text(feat) for feat in input_features if self._normalize_text(feat)]

        # 统计每个菜系的匹配次数
        cuisine_counts = defaultdict(int)
        for feat in normalized_inputs:
            for cuisine in self.feature_map.get(feat, []):
                cuisine_counts[cuisine] += 1

        # 按匹配次数排序（从高到低）
        sorted_cuisines = [
            {"cuisine": cuisine, "count": count}
            for cuisine, count in sorted(cuisine_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return sorted_cuisines[:top_n]
def test_dish_based_cuisine_classifier():
    """测试 DishBasedCuisineClassifier 类"""
# 创建分类器实例
classifier = DishBasedCuisineClassifier()

print("=== 测试 DishBasedCuisineClassifier ===")

# 测试1: 通过特色菜识别菜系
print("\n测试1: 通过特色菜识别菜系")
test_cases = [
    "我想吃麻婆豆腐和水煮鱼",  # 应该识别为川菜
    "来一份宫保鸡丁和夫妻肺片",  # 应该识别为川菜
    "我想吃剁椒鱼头和小炒黄牛肉",  # 应该识别为湘菜
    "来点白切鸡和烧鹅",  # 应该识别为粤菜
    "我想吃锅包肉和小鸡炖蘑菇",  # 应该识别为东北菜
    "来份寿司和刺身",  # 应该识别为日料
]

for text in test_cases:
    cuisine = classifier._extract_cuisine_from_text(text)
    print(f"输入: '{text}' -> 识别菜系: {cuisine}")

# 测试2: 通过同义词识别菜系
print("\n测试2: 通过同义词识别菜系")
synonym_cases = [
    "想吃四川菜",  # 川菜的同义词
    "来点湖南菜",  # 湘菜的同义词
    "吃点广东菜",  # 粤菜的同义词
    "整点日本料理",  # 日料的同义词
]

for text in synonym_cases:
    cuisine = classifier._extract_cuisine_from_text(text)
    print(f"输入: '{text}' -> 识别菜系: {cuisine}")

# 测试3: 通过口味特点识别菜系
print("\n测试3: 通过口味特点识别菜系")
taste_cases = [
    "喜欢麻辣口味的菜",  # 川菜特点
    "偏爱香辣和酸辣",  # 湘菜特点
    "喜欢清淡鲜甜的",  # 粤菜特点
    "喜欢咸鲜和酱香",  # 东北菜特点
    "喜欢鲜咸和清淡",  # 日料特点
]

for text in taste_cases:
    cuisine = classifier._extract_cuisine_from_text(text)
    print(f"输入: '{text}' -> 识别菜系: {cuisine}")

# 测试4: 测试 infer_cuisine 方法
print("\n测试4: 测试 infer_cuisine 方法")
feature_tests = [
    ["麻婆豆腐", "麻辣", "鱼香味"],  # 应该返回川菜
    ["浓油赤酱", "腌笃鲜", "咸中带甜"],  # 应该返回本帮菜
    ["湖南菜", "剁椒胖头鱼", "酸辣味"],  # 应该返回湘菜
    ["番茄炒蛋", "清淡鲜爽"],  # 可能返回粤菜、本帮菜等
]

for features in feature_tests:
    result = classifier.infer_cuisine(features)
    print(f"输入特征: {features} -> 推断结果: {result}")

# 测试5: 测试 handle 方法
print("\n测试5: 测试 handle 方法")
context_tests = [
    {"input_text": "我想吃麻婆豆腐"},
    {"input_text": "来点白切鸡"},
    {"slots": {"菜系": "川菜"}},  # 已有菜系信息
    {"input_text": "吃点不辣的"},  # 不包含菜系信息
]

for i, context in enumerate(context_tests):
    print(f"\n测试5.{i+1}: 输入上下文: {context}")
    # 创建处理器链
    handler = DishBasedCuisineClassifier()
    try:
        result_context = handler.handle(context)
        print(f"输出上下文: {result_context.get('slots', {})}")
    except Exception as e:
        print(f"处理出错: {e}")

if __name__ == "__main__":
    test_dish_based_cuisine_classifier()