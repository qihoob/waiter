import os
import json
import logging
from typing import Optional, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from dict.ltp_tokenizer import get_tokenizer

# 配置日志
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

    # 统一意图列表命名
    DEFAULT_INTENTS = [
        "order_food", "recommend_game", "recommend_dish",
        "festival_recommend", "query_nutrition", "child_or_elderly",
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
            ('clf', LogisticRegression(random_state=42, max_iter=1000))
        ])

    def _get_data_path(self):
        """获取训练数据路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, "intent_data.json")

    def _get_model_dir(self):
        """获取模型存储目录"""
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上一级目录
        return os.path.join(current_dir, "model")

    def load_training_data(self):
        """加载训练数据"""
        data_path = self._get_data_path()
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"训练数据文件不存在: {data_path}")
            
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        texts = [item['text'] for item in data]
        intents = [item['intent'] for item in data]
        
        return texts, intents

    def train(self, texts: Optional[List[str]] = None, intents: Optional[List[str]] = None):
        """训练模型"""
        try:
            # 如果没有提供训练数据，则从文件加载
            if texts is None or intents is None:
                texts, intents = self.load_training_data()
                
            # 分词处理
            tokenized_texts = [' '.join(self.tokenizer.tokenize(text)) for text in texts]
            
            # 训练模型
            self.model.fit(tokenized_texts, intents)
            logger.info("意图分类模型训练完成")
            
            # 保存模型
            self.save_model()
            
        except Exception as e:
            logger.error(f"模型训练失败: {e}")
            raise

    def save_model(self):
        """保存训练好的模型"""
        try:
            import pickle
            
            model_dir = self._get_model_dir()
            os.makedirs(model_dir, exist_ok=True)
            
            model_path = os.path.join(model_dir, self.DEFAULT_MODEL_FILENAME)
            
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
                
            logger.info(f"模型已保存到: {model_path}")
            
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
            raise

    def load_model(self):
        """加载已保存的模型"""
        try:
            import pickle
            
            model_dir = self._get_model_dir()
            model_path = os.path.join(model_dir, self.DEFAULT_MODEL_FILENAME)
            
            if not os.path.exists(model_path):
                logger.warning(f"模型文件不存在: {model_path}")
                return False
                
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
                
            logger.info(f"模型已从 {model_path} 加载")
            return True
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            return False
