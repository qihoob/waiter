# intent/predictor.py
import os
import logging
import joblib

# 导入自定义分词器
from dict.ltp_tokenizer import get_tokenizer

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化分词器
tokenizer = get_tokenizer()

from prompt_builder import INTENT_KEYWORDS


class IntentPredictor:
    """
    意图分类器预测模块

    特性：
    - 加载预训练模型进行意图预测
    - 支持关键词匹配增强
    - 支持句法结构增强
    - 支持槽位信息增强
    """

    # 权重常量
    KEYWORD_MATCH_BONUS = 0.5
    HEALTH_PREF_LOW_FAT = 0.3
    HEALTH_PREF_HIGH_PROTEIN = 0.3
    HEALTH_PREF_SUGAR_FREE = 0.3

    # 默认返回意图
    DEFAULT_FALLBACK_INTENT = "enhanced_basic_with_all"

    def __init__(self, model_path=None):
        """初始化预测器"""
        self.model = None
        self.is_loaded = False
        self.tokenizer = tokenizer

        # 获取模型路径
        if model_path:
            self.load_model(model_path)
        else:
            self.load_default_model()

    def _get_model_dir(self):
        """获取模型存储目录"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "model")

    def _get_default_model_path(self):
        """获取默认模型路径"""
        model_dir = self._get_model_dir()
        return os.path.join(model_dir, "intent_classifier_model.pkl")

    def load_model(self, model_path):
        """加载指定路径的模型"""
        try:
            self.model = joblib.load(model_path)
            self.is_loaded = True
            logger.info(f"模型已加载: {model_path}")
        except Exception as e:
            raise FileNotFoundError(f"无法加载模型文件: {model_path}, 错误: {str(e)}")

    def load_default_model(self):
        """加载默认路径的模型"""
        default_model_path = self._get_default_model_path()
        if os.path.exists(default_model_path):
            self.load_model(default_model_path)
        else:
            logger.warning(f"默认模型不存在: {default_model_path}")

    def _chinese_tokenize(self, text):
        """中文分词处理"""
        return self.tokenizer.tokenize(text)
    def extract_intents_from_keywords(self, text):
        """
        从文本中提取匹配的关键词意图

        Args:
            text: 用户输入文本

        Returns:
            list: 匹配到的意图列表
        """
        matched_intents = []

        # 确保INTENT_KEYWORDS存在且是字典类型
        if isinstance(INTENT_KEYWORDS, dict):
            for intent, keywords in INTENT_KEYWORDS.items():
                if isinstance(keywords, list):
                    for keyword in keywords:
                        if keyword in text and keyword.strip():
                            matched_intents.append(intent)
                            break  # 当前意图匹配成功，检查下一个意图

        return list(set(matched_intents))  # 去重

    def enhance_intent_scores_with_syntax(self, text, intent_scores):
        """
        使用句法分析增强意图得分（当前为占位方法，后续可实现具体逻辑）

        Args:
            text: 用户输入文本
            intent_scores: 当前意图得分字典

        Returns:
            dict: 更新后的意图得分
        """
        # TODO: 后续可以实现具体的句法分析增强逻辑
        return intent_scores
    def classify(self, text, slots=None, is_tokenized=False):
        """
        分类意图

        Args:
            text: 输入文本（可能是原始文本或已分词文本）
            slots: 可选，槽位信息
            is_tokenized: 表示输入文本是否已分词，默认为 False

        Returns:
            str: 识别的意图
        """
        if not self.is_loaded:
            raise Exception("模型未加载，请确保已训练或提供模型路径")

        # 如果未分词，则执行分词操作
        if not is_tokenized:
            processed_text = self._chinese_tokenize(text)
        else:
            processed_text = text  # 直接使用已分词结果

        probs = self.model.predict_proba([processed_text])[0]
        classes = self.model.named_steps['clf'].classes_

        intent_scores = {cls: prob for cls, prob in zip(classes, probs)}

        # 关键词匹配得分增强
        keyword_intents = self.extract_intents_from_keywords(text if not is_tokenized else text[:20])
        for intent in keyword_intents:
            intent_scores[intent] = intent_scores.get(intent, 0) + self.KEYWORD_MATCH_BONUS

        # 句法分析得分增强
        intent_scores = self.enhance_intent_scores_with_syntax(text if not is_tokenized else text[:20], intent_scores)

        # 槽位信息增强
        if slots:
            health_pref = slots.get("健康偏好")
            if health_pref == "低脂":
                intent_scores["weight_loss"] = intent_scores.get("weight_loss", 0) + self.HEALTH_PREF_LOW_FAT
            elif health_pref == "高蛋白":
                intent_scores["fitness_nutrition"] = intent_scores.get("fitness_nutrition", 0) + self.HEALTH_PREF_HIGH_PROTEIN
            elif health_pref == "无糖":
                intent_scores["intermittent_fasting"] = intent_scores.get("intermittent_fasting", 0) + self.HEALTH_PREF_SUGAR_FREE

        # 排序并输出所有意图
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)

        # 记录调试信息
        logger.info("【意图识别结果】")
        for intent, score in sorted_intents:
            logger.info(f"{intent}: {score:.4f}")

        return sorted_intents[0][0] if sorted_intents else self.DEFAULT_FALLBACK_INTENT


if __name__ == '__main__':
    # 测试意图分类器
    predictor = IntentPredictor()

    # 测试文本
    test_text = "我想吃低脂的食物，最好是高蛋白的"
    slots = {"健康偏好": "低脂"}

    # 进行意图分类
    intent = predictor.classify(test_text, slots)
    print(f"识别的意图: {intent}")

    tokenized_text = tokenizer.tokenize("我想吃低脂的食物，最好是高蛋白的")
    predictor.classify(tokenized_text, slots, is_tokenized=True)