# E:\work\waiter\slot\CuisineFlavorHandler.py
from typing import Dict, Any, List, Optional
from slot.SlotHandler import SlotHandler
from prompt_builder.features_dict import cuisine_complete_info
from fuzzywuzzy import process
import logging
import re

logger = logging.getLogger(__name__)

class CuisineFlavorHandler(SlotHandler):
    """菜系口味信息处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 构建菜系标准化映射
        self.cuisine_mapping = {}
        # 构建所有菜系名称和同义词列表
        self.all_cuisine_names = []
        for cuisine_name, details in cuisine_complete_info.items():
            # 标准菜系名映射到自身
            self.cuisine_mapping[cuisine_name] = cuisine_name
            self.all_cuisine_names.append(cuisine_name)

            # 同义词映射到标准菜系名
            for synonym in details.get("同义词", []):
                self.cuisine_mapping[synonym] = cuisine_name
                self.all_cuisine_names.append(synonym)

    def handle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 从上下文中获取已识别的菜系
            slots = context.get('slots', {})
            cuisine = slots.get('菜系')

            # 如果没有识别到菜系，尝试从输入文本中识别
            if not cuisine:
                cuisine = self._extract_cuisine_from_text(context)
                if cuisine:
                    slots['菜系'] = cuisine

            # 如果识别到菜系，获取详细信息
            if cuisine:
                cuisine_info = self._get_cuisine_info(cuisine)
                if cuisine_info:
                    # 将详细信息添加到上下文
                    context['cuisine_info'] = cuisine_info

                    # 提取特色菜
                    special_dish = self._extract_special_dish(context, cuisine_info.get("特色菜", []))
                    if special_dish:
                        slots['特色菜'] = special_dish

                    # 提取家常菜
                    home_dish = self._extract_home_dish(context, cuisine_info.get("家常菜", []))
                    if home_dish:
                        slots['家常菜'] = home_dish

                    # 提取核心口味
                    core_taste = self._extract_core_taste(context, cuisine_info.get("口味特点", {}).get("核心口味", []))
                    if core_taste:
                        slots['核心口味'] = core_taste

                    # 提取味型细分
                    taste_subtype = self._extract_taste_subtype(context, cuisine_info.get("口味特点", {}).get("味型细分", []))
                    if taste_subtype:
                        slots['味型细分'] = taste_subtype

                    # 获取菜系说明
                    cuisine_description = cuisine_info.get("说明", "")
                    if cuisine_description:
                        slots['菜系说明'] = cuisine_description

                    # 获取口味特点描述
                    taste_description = cuisine_info.get("口味特点", {}).get("特点描述", "")
                    if taste_description:
                        slots['口味特点'] = taste_description

            context['slots'] = slots

        except Exception as e:
            logger.warning(f"处理菜系口味信息时出错: {e}")

        return super().handle(context)

    def _extract_cuisine_from_text(self, context: Dict[str, Any]) -> Optional[str]:
        """
        从输入文本中提取菜系信息

        Args:
            context: 处理上下文

        Returns:
            str: 识别到的菜系（标准化后的名称）
        """
        # 按照指定顺序获取文本数据
        texts = []

        # 优先级1: cleaned_text
        if 'cleaned_text' in context and context['cleaned_text']:
            texts.append(context['cleaned_text'])

        # 优先级2: input_text
        if 'input_text' in context and context['input_text']:
            texts.append(context['input_text'])

        # 优先级3: tokenized_text
        if 'tokenized_text' in context and context['tokenized_text']:
            texts.append(context['tokenized_text'])

        # 按照指定顺序在每个文本中查找菜系
        for text in texts:
            if not text:
                continue

            # 使用模糊匹配查找最可能的菜系
            try:
                matched_cuisine, score = process.extractOne(text, self.all_cuisine_names)
                if score >= 80:  # 设置匹配阈值
                    # 返回标准化的菜系名称
                    return self.cuisine_mapping.get(matched_cuisine, matched_cuisine)
            except Exception as e:
                logger.warning(f"菜系模糊匹配出错: {e}")

            # 精确匹配
            for cuisine_name in self.all_cuisine_names:
                if cuisine_name in text:
                    # 返回标准化的菜系名称
                    return self.cuisine_mapping.get(cuisine_name, cuisine_name)

        return None

    def _get_cuisine_info(self, cuisine: str) -> Optional[Dict[str, Any]]:
        """
        获取菜系的详细信息

        Args:
            cuisine: 标准化后的菜系名称

        Returns:
            dict: 菜系详细信息
        """
        # 获取标准化菜系名称
        standard_cuisine = self.cuisine_mapping.get(cuisine, cuisine)

        # 从cuisine_complete_info中获取详细信息
        if standard_cuisine in cuisine_complete_info:
            return cuisine_complete_info[standard_cuisine]

        return None

    def _extract_special_dish(self, context: Dict[str, Any], special_dishes: List[Dict[str, Any]]) -> Optional[str]:
        """
        从上下文中提取特色菜信息

        Args:
            context: 处理上下文
            special_dishes: 特色菜列表

        Returns:
            str: 识别到的特色菜名称
        """
        # 获取文本数据
        texts = []
        if 'input_text' in context:
            texts.append(context['input_text'])
        if 'cleaned_text' in context:
            texts.append(context['cleaned_text'])
        if 'tokenized_text' in context:
            texts.append(context['tokenized_text'])

        # 构建特色菜名称列表（包括同义词）
        all_dish_names = []
        dish_mapping = {}  # 同义词到标准名称的映射

        for dish in special_dishes:
            dish_name = dish["名称"]
            all_dish_names.append(dish_name)
            dish_mapping[dish_name] = dish_name

            for synonym in dish.get("同义词", []):
                all_dish_names.append(synonym)
                dish_mapping[synonym] = dish_name

        # 在每个文本中查找特色菜
        for text in texts:
            if not text:
                continue

            # 精确匹配
            for dish_name in all_dish_names:
                if dish_name in text:
                    return dish_mapping[dish_name]

            # 模糊匹配
            try:
                matched_dish, score = process.extractOne(text, all_dish_names)
                if score >= 85:  # 更高的匹配阈值
                    return dish_mapping[matched_dish]
            except Exception as e:
                logger.warning(f"特色菜模糊匹配出错: {e}")

        return None

    def _extract_home_dish(self, context: Dict[str, Any], home_dishes: List[Dict[str, Any]]) -> Optional[str]:
        """
        从上下文中提取家常菜信息

        Args:
            context: 处理上下文
            home_dishes: 家常菜列表

        Returns:
            str: 识别到的家常菜名称
        """
        # 获取文本数据
        texts = []
        if 'input_text' in context:
            texts.append(context['input_text'])
        if 'cleaned_text' in context:
            texts.append(context['cleaned_text'])
        if 'tokenized_text' in context:
            texts.append(context['tokenized_text'])

        # 构建家常菜名称列表（包括同义词）
        all_dish_names = []
        dish_mapping = {}  # 同义词到标准名称的映射

        for dish in home_dishes:
            dish_name = dish["名称"]
            all_dish_names.append(dish_name)
            dish_mapping[dish_name] = dish_name

            for synonym in dish.get("同义词", []):
                all_dish_names.append(synonym)
                dish_mapping[synonym] = dish_name

        # 在每个文本中查找家常菜
        for text in texts:
            if not text:
                continue

            # 精确匹配
            for dish_name in all_dish_names:
                if dish_name in text:
                    return dish_mapping[dish_name]

            # 模糊匹配
            try:
                matched_dish, score = process.extractOne(text, all_dish_names)
                if score >= 85:  # 更高的匹配阈值
                    return dish_mapping[matched_dish]
            except Exception as e:
                logger.warning(f"家常菜模糊匹配出错: {e}")

        return None

    def _extract_core_taste(self, context: Dict[str, Any], core_tastes: List[str]) -> Optional[str]:
        """
        从上下文中提取核心口味信息

        Args:
            context: 处理上下文
            core_tastes: 核心口味列表

        Returns:
            str: 识别到的核心口味
        """
        # 获取文本数据
        texts = []
        if 'input_text' in context:
            texts.append(context['input_text'])
        if 'cleaned_text' in context:
            texts.append(context['cleaned_text'])
        if 'tokenized_text' in context:
            texts.append(context['tokenized_text'])

        # 在每个文本中查找核心口味
        for text in texts:
            if not text:
                continue

            # 精确匹配
            for taste in core_tastes:
                if taste in text:
                    return taste

            # 模糊匹配
            try:
                matched_taste, score = process.extractOne(text, core_tastes)
                if score >= 85:  # 更高的匹配阈值
                    return matched_taste
            except Exception as e:
                logger.warning(f"核心口味模糊匹配出错: {e}")

        return None

    def _extract_taste_subtype(self, context: Dict[str, Any], taste_subtypes: List[str]) -> Optional[str]:
        """
        从上下文中提取味型细分信息

        Args:
            context: 处理上下文
            taste_subtypes: 味型细分列表

        Returns:
            str: 识别到的味型细分
        """
        # 获取文本数据
        texts = []
        if 'input_text' in context:
            texts.append(context['input_text'])
        if 'cleaned_text' in context:
            texts.append(context['cleaned_text'])
        if 'tokenized_text' in context:
            texts.append(context['tokenized_text'])

        # 提取味型关键词（从"鱼香味（酸甜辣平衡）"中提取"鱼香味"）
        taste_subtype_keywords = []
        for subtype in taste_subtypes:
            match = re.match(r"^(.+?)(?:\(|\s)", subtype)
            if match:
                taste_subtype_keywords.append(match.group(1))
            else:
                taste_subtype_keywords.append(subtype)

        # 在每个文本中查找味型细分
        for text in texts:
            if not text:
                continue

            # 精确匹配
            for keyword in taste_subtype_keywords:
                if keyword in text:
                    return keyword

            # 模糊匹配
            try:
                matched_keyword, score = process.extractOne(text, taste_subtype_keywords)
                if score >= 85:  # 更高的匹配阈值
                    return matched_keyword
            except Exception as e:
                logger.warning(f"味型细分模糊匹配出错: {e}")

        return None

# 测试代码
def test_cuisine_flavor_handler():
    """测试菜系口味处理器"""
    print("=" * 50)
    print("测试菜系口味处理器")
    print("=" * 50)

    # 创建处理器实例
    handler = CuisineFlavorHandler()

    # 测试用例
    test_cases = [
        {
            "name": "识别川菜及其特色",
            "context": {
                "cleaned_text": "我想吃麻婆豆腐，听说是川菜"
            }
        },
        {
            "name": "识别粤菜及其口味",
            "context": {
                "cleaned_text": "我想吃清淡一点的白切鸡"
            }
        },
        {
            "name": "识别湘菜及其家常菜",
            "context": {
                "cleaned_text": "来一份湘菜的农家小炒肉"
            }
        },
        {
            "name": "识别东北菜及其说明",
            "context": {
                "cleaned_text": "我想吃东北菜，要口味浓郁的"
            }
        },
        {
            "name": "识别日料及其味型",
            "context": {
                "cleaned_text": "我想吃寿司，要鲜咸口味的"
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
            print(f"识别到的菜系: {slots.get('菜系', '未识别到')}")
            print(f"特色菜: {slots.get('特色菜', '未识别到')}")
            print(f"家常菜: {slots.get('家常菜', '未识别到')}")
            print(f"核心口味: {slots.get('核心口味', '未识别到')}")
            print(f"味型细分: {slots.get('味型细分', '未识别到')}")
            print(f"菜系说明: {slots.get('菜系说明', '无')}")
            print(f"口味特点: {slots.get('口味特点', '无')}")

        except Exception as e:
            print(f"处理出错: {e}")


if __name__ == "__main__":
    test_cuisine_flavor_handler()
