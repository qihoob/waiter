# E:\work\waiter\slot\CuisineFlavorHandler.py
from typing import Dict, Any
from slot.SlotHandler import SlotHandler
from prompt_builder.features_dict import cuisine_flavors, cuisine_synonym_dict
from fuzzywuzzy import process
import logging

logger = logging.getLogger(__name__)

class CuisineFlavorHandler(SlotHandler):
    """菜系口味信息处理器"""

    def __init__(self, next_handler=None):
        super().__init__(next_handler)
        # 构建菜系标准化映射
        self.cuisine_mapping = {}
        for standard_cuisine, synonyms in cuisine_synonym_dict.items():
            # 标准菜系名映射到自身
            self.cuisine_mapping[standard_cuisine] = standard_cuisine
            # 同义词映射到标准菜系名
            for synonym in synonyms:
                self.cuisine_mapping[synonym] = standard_cuisine

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

            # 如果识别到菜系，获取口味信息
            if cuisine:
                flavor_info = self._get_cuisine_flavor_info(cuisine)
                if flavor_info:
                    # 将口味信息添加到上下文
                    slots['核心口味'] = flavor_info.get('核心口味')
                    slots['口味特点'] = flavor_info.get('口味特点')
                    # 也可以将完整口味信息保存到上下文供后续使用
                    context['cuisine_flavor_info'] = flavor_info

            context['slots'] = slots

        except Exception as e:
            logger.warning(f"处理菜系口味信息时出错: {e}")

        return super().handle(context)

    def _extract_cuisine_from_text(self, context: Dict[str, Any]) -> str:
        """
        从输入文本中提取菜系信息，按照 cleaned_text、input_text、tokenized_text 的顺序依次识别

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

        # 收集所有可能的菜系名称（包括标准名和同义词）
        all_cuisine_names = list(cuisine_synonym_dict.keys())  # 标准菜系名
        for synonyms in cuisine_synonym_dict.values():
            all_cuisine_names.extend(synonyms)  # 同义词

        # 按照指定顺序在每个文本中查找菜系
        for text in texts:
            if not text:
                continue

            # 使用模糊匹配查找最可能的菜系
            try:
                matched_cuisine, score = process.extractOne(text, all_cuisine_names)
                if score >= 80:  # 设置匹配阈值
                    # 返回标准化的菜系名称
                    return self.cuisine_mapping.get(matched_cuisine, matched_cuisine)
            except Exception as e:
                logger.warning(f"菜系模糊匹配出错: {e}")

            # 精确匹配
            for cuisine_name in all_cuisine_names:
                if cuisine_name in text:
                    # 返回标准化的菜系名称
                    return self.cuisine_mapping.get(cuisine_name, cuisine_name)

        return None

    def _get_cuisine_flavor_info(self, cuisine: str) -> Dict[str, Any]:
        """
        获取菜系的口味信息

        Args:
            cuisine: 标准化后的菜系名称

        Returns:
            dict: 菜系口味信息
        """
        # 获取标准化菜系名称
        standard_cuisine = self.cuisine_mapping.get(cuisine, cuisine)

        # 从cuisine_flavors中获取口味信息
        if standard_cuisine in cuisine_flavors:
            flavor_info = cuisine_flavors[standard_cuisine]
            return {
                '菜系': standard_cuisine,
                '核心口味': flavor_info.get('核心口味', []),
                '口味特点': flavor_info.get('口味特点', ''),
                '味型细分': flavor_info.get('味型细分', [])
            }

        return None
