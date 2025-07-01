# collector/nlu/intent_classifier.py

class IntentClassifier:
    def __init__(self):
        """
        初始化意图识别规则库
        """
        self.intent_rules = {
            "order": [
                "下单", "点菜", "订位", "订桌", "订好了", "订过",
                "订座", "订餐", "点了", "选好了", "确定了"
            ],
            "game_recommendation": [
                "玩什么", "打麻将", "斗地主", "狼人杀", "真心话大冒险",
                "你画我猜", "谁是卧底", "拼图游戏", "情侣互动游戏"
            ],
            "healthy_diet": [
                "低脂", "清淡", "高蛋白", "无糖", "控油", "控卡", "减脂",
                "轻食", "健身餐", "少油少盐"
            ],
            "festival": [
                "情人节", "七夕", "圣诞节", "元旦", "春节", "生日宴", "纪念日"
            ],
            "weather_based": [
                "冷", "热", "下雨", "刮风", "天太热", "天太冷"
            ],
            "vegetarian": [
                "素食", "不吃肉", "不吃荤", "素斋", "纯素"
            ],
            "child_or_elderly": [
                "带小孩", "老人", "儿童", "宝宝", "长者"
            ]
        }

    def classify(self, text, slots=None):
        """
        根据文本内容和槽位信息判断意图
        :param text: 用户原始输入文本
        :param slots: 已提取的槽位字典
        :return: 最可能的意图
        """
        scores = {}

        # 1. 基于关键词匹配计算分数
        for intent, keywords in self.intent_rules.items():
            score = sum(1 for word in keywords if word in text)
            scores[intent] = score

        # 2. 结合槽位进一步增强判断
        if slots:
            if "健康偏好" in slots:
                scores["healthy_diet"] += 2
            if "特殊节日" in slots:
                scores["festival"] += 3
            if "忌口" in slots and any(word in slots["忌口"] for word in ["素食", "不吃肉"]):
                scores["vegetarian"] += 2
            if "就餐形式" in slots and "自助餐" in slots["就餐形式"]:
                scores["order"] += 1

        # 3. 如果有多个意图得分相同，优先返回以下顺序中的第一个
        priority_order = [
            "festival", "game_recommendation",
            "healthy_diet", "vegetarian",
            "order", "weather_based",
            "child_or_elderly"
        ]

        # 4. 计算最高分意图
        best_intent = max(scores, key=scores.get)
        highest_score = scores[best_intent]

        # 若多个意图得分相同，按优先级排序
        tied_intents = [intent for intent, score in scores.items() if score == highest_score]
        if len(tied_intents) > 1:
            for intent in priority_order:
                if intent in tied_intents:
                    return intent

        return best_intent
