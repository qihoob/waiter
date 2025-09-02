# intent/trainer.py
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import json
from collections import defaultdict
import os
import logging
import joblib

# 导入自定义分词器
from dict.ltp_tokenizer import  get_tokenizer

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntentTrainer:
    """
    意图分类器训练模块

    特性：
    - 使用TF-IDF + 逻辑回归进行意图分类训练
    - 支持中文分词处理（基于LTP）
    - 支持模型持久化存储
    """

    # 默认意图列表
    DEFAULT_INTENTS = [
        "order", "game_recommendation", "healthy_diet",
        "festival", "vegetarian", "child_or_elderly",
        "weight_loss", "intermittent_fasting", "seasonal_food",
        "fitness_nutrition", "holiday_event", "group_gathering",
        "takeaway_service", "allergy_safe", "nutritional_info"
    ]

    # 默认模型文件名
    DEFAULT_MODEL_FILENAME = "intent_classifier_model.pkl"

    def __init__(self, model_path: Optional[str] = None):
        """初始化训练器"""
        self.model = self._build_pipeline()
        self.tokenizer = get_tokenizer(model_path)

    def _build_pipeline(self):
        """构建机器学习管道"""
        return Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', LogisticRegression())
        ])

    def _get_data_path(self):
        """获取训练数据路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "intent_data.json")

    def _get_model_dir(self):
        """获取模型存储目录"""
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上一级目录
        return os.path.join(current_dir, "model")

    def _chinese_tokenize(self, text: str) -> str:
        """
        使用LTP进行中文分词处理

        Args:
            text: 输入文本

        Returns:
            str: 分词后的字符串
        """
        return self.tokenizer.tokenize(text)

    def _batch_tokenize(self, texts: List[str]) -> List[str]:
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
            # 执行批量分词
            return self.tokenizer.batch_tokenize(texts)
        except Exception as e:
            logger.error(f"批量分词出错: {e}", exc_info=True)
            # 出错时退化为逐条处理
            return [self._chinese_tokenize(text) for text in texts]

    def train(self, model_filename: Optional[str] = None) -> str:
        """
        训练意图分类模型

        Args:
            model_filename: 可选，自定义模型文件名

        Returns:
            str: 模型保存路径
        """
        model_filename = model_filename or self.DEFAULT_MODEL_FILENAME

        data_path = self._get_data_path()
        model_dir = self._get_model_dir()

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"训练数据文件未找到: {data_path}")
        except json.JSONDecodeError:
            raise ValueError(f"JSON 解析失败: {data_path}")

        texts = [item["text"] for item in data]
        labels = [item["intent"] for item in data]

        # 使用批量分词方法
        processed_texts = self._batch_tokenize(texts)

        self.model.fit(processed_texts, labels)

        # 确保模型目录存在
        os.makedirs(model_dir, exist_ok=True)

        # 保存模型
        model_path = os.path.join(model_dir, model_filename)
        joblib.dump(self.model, model_path)

        logger.info(f"模型训练完成并保存至: {model_path}")
        return model_path


if __name__ == "__main__":
    trainer = IntentTrainer()
    trainer.train()
