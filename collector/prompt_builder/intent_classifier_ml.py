from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import jieba
import json
from ltp import LTP
from collections import defaultdict

ltp = LTP()

from collector.prompt_builder.config import INTENT_KEYWORDS, KEYWORD_WEIGHT_RULES


class IntentClassifierML:
    def __init__(self, model_path=None):
        self.intents = [
            "order", "game_recommendation", "healthy_diet",
            "festival", "vegetarian", "child_or_elderly",
            "weight_loss", "intermittent_fasting", "seasonal_food",
            "fitness_nutrition", "holiday_event", "group_gathering",
            "takeaway_service", "allergy_safe", "nutritional_info"
        ]
        self.model = self._build_pipeline()
        self.is_trained = False


    def _build_pipeline(self):
        return Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', LogisticRegression())
        ])

    def _chinese_tokenize(self, text):
        return ' '.join(jieba.cut(text))

    def train(self):
        with open("E:\\work\\waiter\\collector\\prompt_builder\\ml_data\intent_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        texts = [item["text"] for item in data]
        labels = [item["intent"] for item in data]
        processed_texts = [self._chinese_tokenize(t) for t in texts]
        self.model.fit(processed_texts, labels)
        self.is_trained = True

    def classify(self, text, slots=None):
        if not self.is_trained:
            raise Exception("模型未训练，请先调用 train() 方法")

        processed_text = self._chinese_tokenize(text)

        probs = self.model.predict_proba([processed_text])[0]
        classes = self.model.named_steps['clf'].classes_

        intent_scores = defaultdict(float)
        for cls, prob in zip(classes, probs):
            intent_scores[cls] = prob

        keyword_intents = self.extract_intents_from_keywords(text)
        for intent in keyword_intents:
            intent_scores[intent] += 0.5

        # 新增：语法结构增强
        intent_scores = self.enhance_intent_scores_with_syntax(text, intent_scores)

        # 槽位增强
        if slots:
            if "健康偏好" in slots:
                health_pref = slots["健康偏好"]
                if health_pref == "低脂":
                    intent_scores["weight_loss"] += 0.3
                elif health_pref == "高蛋白":
                    intent_scores["fitness_nutrition"] += 0.3
                elif health_pref == "无糖":
                    intent_scores["intermittent_fasting"] += 0.3

        # 排序并输出所有意图
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)

        # 打印所有意图及得分（可选）
        print("【意图识别结果】")
        for intent, score in sorted_intents:
            print(f"{intent}: {score:.4f}")

        # 返回得分最高的意图
        if sorted_intents:
            best_intent, best_score = sorted_intents[0]
            return best_intent
        else:
            return "enhanced_basic_with_all"
    def extract_intents_from_keywords(self, text):
        matched_intents = []
        for intent, keywords in INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    matched_intents.append(intent)
                    break
        return list(set(matched_intents))
    def enhance_intent_scores_with_syntax(self, text, intent_scores):
        """
        使用句法分析增强意图得分
        :param text: 用户输入文本
        :param intent_scores: 当前意图得分字典
        :return: 更新后的意图得分
        """
        syntax_result = self.analyze_syntax(text)

        for word, postag, arc in syntax_result:
            head_idx = arc["head"] - 1  # 依存关系头索引（从1开始）
            relation = arc["relation"]

            for intent, rule in KEYWORD_WEIGHT_RULES.items():
                if word in rule["关键词"]:
                    weight = rule.get("位置权重", {}).get(relation, 0.1)  # 默认权重
                    intent_scores[intent] += weight

        return intent_scores

    def analyze_syntax(self, text):
        """
        使用 LTP 4.x 分析中文句法结构
        :param text: 输入文本
        :return: list of (word, postag, head, relation)
        """
    # 调用 pipeline 执行分词、词性标注、依存句法分析
        output = ltp.pipeline([text], tasks=["tok", "pos", "dep"])

        words = output.tok[0]
        postags = output.pos[0]
        deps = output.dep[0]

        # 构建依存关系结构
        arcs = [{"head": dep["head"] - 1, "relation": dep["rel"]} for dep in deps]  # head 转换为从0开始索引

        return list(zip(words, postags, arcs))
