"""
ltp_tokenizer.py - 基于LTP的中文分词模块
"""

import os
import json
import logging
from functools import lru_cache
from typing import List, Tuple, Optional, Dict, Any
from ltp import LTP
import threading  # 导入线程模块


# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 新增常量：默认词典文件名
DEFAULT_DICT_NAME = "user_dict.txt"

# 中文数字映射表
CHINESE_NUMBERS = {
    '零': 0, '〇': 0, '一': 1, '二': 2, '两': 2,
    '三': 3, '四': 4, '五': 5, '六': 6,
    '七': 7, '八': 8, '九': 9, '十': 10,
    '十一': 11, '十二': 12, '十三': 13, '十四': 14,
    '十五': 15, '十六': 16, '十七': 17, '十八': 18,
    '十九': 19, '二十': 20, '三十': 30, '四十': 40,
    '五十': 50, '六十': 60, '七十': 70, '八十': 80,
    '九十': 90, '百': 100, '佰': 100, '千': 1000, '仟': 1000
}

# 数字替换规则
NUMBER_REPLACEMENT_RULES = {
    # 英文数字转中文
    'zero': '0', 'one': '1', 'two': '2', 'three': '3',
    'four': '4', 'five': '5', 'six': '6', 'seven': '7',
    'eight': '8', 'nine': '9', 'ten': '10',

    # 常见英文数字缩写
    'k': '千', '万': '万', 'm': '百万'
}


# 全局LTP实例（单例模式）
_ltp_instance = None

# 全局锁用于确保多线程环境下的安全初始化
_tokenizer_lock = threading.Lock()  # 新增线程锁
_global_tokenizer = None


def get_ltp_instance(model_path: Optional[str] = None) -> LTP:
    """
    获取LTP实例（单例模式）

    Args:
        model_path: 可选，自定义模型路径

    Returns:
        LTP: LTP实例
    """
    global _ltp_instance

    if _ltp_instance is None:
        try:
            if model_path:
                _ltp_instance = LTP(path=model_path)
                logger.info(f"使用指定路径加载LTP模型: {model_path}")
            else:
                _ltp_instance = LTP()
                logger.info("使用默认路径加载LTP模型")
        except Exception as e:
            raise RuntimeError(f"LTP初始化失败: {e}")

    return _ltp_instance


class ChineseTokenizer:
    """
    基于LTP的中文分词管理器

    特性：
    - 支持中文分词处理
    - 支持批量分词
    - 支持缓存提升性能
    - 支持词性标注
    - 支持依存句法分析
    - ✅ 支持自定义词典加载与热更新
    - ✅ 支持中文/英文数字归一化
    """

    def __init__(self, model_path: Optional[str] = None, dict_path: Optional[str] = None):
        """
        初始化中文分词管理器

        Args:
            model_path: 可选，自定义LTP模型路径
            dict_path: 可选，自定义词典路径
        """
        self.ltp = get_ltp_instance(model_path)
        self._tokenize_cache = {}

        # 获取当前文件所在目录作为默认目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.dict_path = dict_path or os.path.join(current_dir, DEFAULT_DICT_NAME)

        self.user_defined_words = set()  # 存储自定义词汇
        self._load_custom_dict()  # 加载自定义词典

    @lru_cache(maxsize=1000)
    def tokenize(self, text: str) -> str:
        """
        对中文文本进行基础分词

        Args:
            text: 输入文本

        Returns:
            str: 分词后的字符串
        """
        if not text:
            return ""

        # 检查缓存
        if text in self._tokenize_cache:
            return self._tokenize_cache[text]

        try:
            # 执行归一化
            normalized_text = self.normalize_input(text)

            # 使用pipeline执行分词任务
            output = self.ltp.pipeline([normalized_text], tasks=["cws"])
            tokens = output.cws[0]  # 获取第一个句子的分词结果

            # 如果有自定义词典，尝试合并匹配
            if self.user_defined_words:
                tokens = self._merge_with_user_dict(tokens)

            # 过滤空格和特殊字符
            filtered_tokens = [token for token in tokens if token.strip()]

            result = ' '.join(filtered_tokens)

            # 更新缓存
            self._tokenize_cache[text] = result

            return result
        except Exception as e:
            logger.error(f"LTP分词出错: {e}", exc_info=True)
            return ""  # 出错时返回空字符串

    def normalize_input(self, text: str) -> str:
        """
        归一化输入文本

        包括：
        - 中文数字转阿拉伯数字
        - 英文数字转中文数字或阿拉伯数字
        - 常见缩写替换
        - 大小写统一

        Args:
            text: 输入文本

        Returns:
            str: 归一化后的文本
        """
        if not text:
            return ""

        # 转换为小写
        text = text.lower()

        # 英文数字替换
        for eng_num, chn_num in NUMBER_REPLACEMENT_RULES.items():
            text = text.replace(eng_num, chn_num)

        # 中文数字转换
        text = self._chinese_number_to_arabic(text)

        return text

    def _chinese_number_to_arabic(self, text: str) -> str:
        """
        中文数字转阿拉伯数字

        Args:
            text: 包含中文数字的文本

        Returns:
            str: 替换为阿拉伯数字的文本
        """
        if not text:
            return ""

        # 简单实现：将常见中文数字替换为阿拉伯数字
        for chn_num, arabic_num in CHINESE_NUMBERS.items():
            text = text.replace(chn_num, str(arabic_num))

        return text

    def _load_custom_dict(self):
        """加载自定义词典"""
        if not self.dict_path:
            logger.info("未提供自定义词典路径，跳过加载")
            return

        try:
            if os.path.exists(self.dict_path):
                with open(self.dict_path, "r", encoding="utf-8") as f:
                    for line in f:
                        word = line.strip()
                        if word:
                            self.user_defined_words.add(word)
                logger.info(f"[INFO] 自定义词典 {self.dict_path} 加载成功，共 {len(self.user_defined_words)} 个词")
            else:
                logger.warning(f"[WARNING] 自定义词典文件不存在: {self.dict_path}")
        except Exception as e:
            logger.error(f"[ERROR] 加载自定义词典失败: {e}", exc_info=True)

    def reload_custom_dict(self):
        """重新加载自定义词典（热加载）"""
        self._tokenize_cache.clear()  # 清除缓存
        self.user_defined_words.clear()  # 清空已有自定义词
        self._load_custom_dict()
        logger.info("[INFO] 自定义词典已重新加载")

    def _merge_with_user_dict(self, tokens: List[str]) -> List[str]:
        """
        将现有分词结果与自定义词典合并

        Args:
            tokens: 当前分词结果

        Returns:
            list: 合并后的分词结果
        """
        # TODO: 更复杂的合并策略可在此实现
        # 示例：简单地插入所有自定义词到分词结果中
        merged = []

        # 简单实现：遍历原文本中的每个词，如果命中自定义词，则保留该词
        words_found = []
        current_text = ' '.join(tokens)

        for word in sorted(self.user_defined_words, key=len, reverse=True):  # 从长到短匹配
            if word in current_text:
                words_found.append(word)
                current_text = current_text.replace(word, '')  # 替换掉已找到的词

        # 合并自定义词和原分词结果
        if words_found:
            merged = words_found + tokens
            return merged

        return tokens

    def batch_tokenize(self, texts: List[str]) -> List[str]:
        """
        批量处理文本分词（显著提升训练效率）

        Args:
            texts: 文本列表

        Returns:
            list: 分词后的文本列表
        """
        if not texts:
            return []

        try:
            # 执行批量分词任务
            output = self.ltp.pipeline(texts, tasks=["cws"])

            # 处理每个分词结果
            processed = [' '.join(token for token in res if token.strip()) for res in output.cws]
            return processed
        except Exception as e:
            logger.error(f"LTP批量分词出错: {e}", exc_info=True)
            # 出错时退化为逐条处理
            return [self.tokenize(text) for text in texts]

    def pos_tag(self, text: str) -> List[Tuple[str, str]]:
        """
        词性标注

        Args:
            text: 输入文本

        Returns:
            list of (word, tag): 单词及其对应的词性标签
        """
        if not text:
            return []

        try:
            # 执行词性标注
            output = self.ltp.pipeline([text], tasks=["cws", "pos"])

            words = output.cws[0]
            tags = output.pos[0]

            return list(zip(words, tags))
        except Exception as e:
            logger.error(f"LTP词性标注出错: {e}", exc_info=True)
            return []

    def dep_parse(self, text: str) -> List[Tuple[str, int, str]]:
        """
        依存句法分析

        Args:
            text: 输入文本

        Returns:
            list of (word, head, relation): 词语、头部索引、关系
        """
        if not text:
            return []

        try:
            # 执行依存句法分析
            output = self.ltp.pipeline([text], tasks=["cws", "pos", "dep"])

            words = output.cws[0]
            deps = output.dep[0]

            # 构建依存关系结构
            arcs = []
            for i, rel in enumerate(deps):
                arcs.append({
                    "head": i + 1,
                    "relation": rel
                })

            # 返回解析结果
            return list(zip(words, [arc["head"] - 1 for arc in arcs], [arc["relation"] for arc in arcs]))
        except Exception as e:
            logger.error(f"LTP依存句法分析出错: {e}", exc_info=True)
            return []


def get_tokenizer(model_path: Optional[str] = None, dict_path: Optional[str] = None) -> ChineseTokenizer:
    """
    获取全局分词器实例（单例模式）

    Args:
        model_path: 可选，自定义模型路径
        dict_path: 可选，自定义词典路径

    Returns:
        ChineseTokenizer: 分词器实例
    """
    global _global_tokenizer
    with _tokenizer_lock:  # 使用锁确保只有一个线程可以进入初始化流程
        if _global_tokenizer is None:
            _global_tokenizer = ChineseTokenizer(model_path, dict_path)

    return _global_tokenizer
