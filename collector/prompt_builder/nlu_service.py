# collector/nlu/intent_classifier.py

class IntentClassifier:
    def __init__(self):
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
            "vegetarian": [
                "素食", "不吃肉", "不吃荤", "素斋", "纯素"
            ],
            "weather_based": [
                "冷", "热", "下雨", "刮风", "天太热", "天太冷"
            ],
            "child_or_elderly": [
                "带小孩", "老人", "儿童", "宝宝", "长者"
            ],
            "weight_loss": [
                "减脂餐", "低卡路里", "减肥", "控制体重", "轻食主义"
            ],
            "intermittent_fasting": [
                "控糖", "轻断食", "低碳水", "无糖", "生酮"
            ],
            "seasonal_food": [
                "夏天", "炎热", "冷饮", "冰镇", "清爽", "冬天", "寒冷", "热乎"
            ],
            "fitness_nutrition": [
                "高蛋白", "增肌", "健身餐", "运动后", "蛋白质补充"
            ],
            "holiday_event": [
                "春节", "周年庆", "纪念日", "情侣节", "团建"
            ],
            "group_gathering": [
                "多人聚餐", "朋友聚会", "家庭聚餐", "公司年会"
            ],
            "takeaway_service": [
                "打包", "外带", "送餐", "外卖", "拿走"
            ],
            "allergy_safe": [
                "不过敏吗", "不含花生", "没有海鲜", "安全食材"
            ],
            "nutritional_info": [
                "多少卡", "热量标注", "营养表", "健康值"
            ]
        }



    def classify(self, text, slots=None):
        scores = {}

        for intent, keywords in self.intent_rules.items():
            score = sum(1 for word in keywords if word in text)
            scores[intent] = score

        # 结合槽位信息增强判断
        if slots:
            if "健康偏好" in slots:
                health_pref = slots["健康偏好"]
                if health_pref == "低脂":
                    scores["weight_loss"] += 3
                elif health_pref == "无糖":
                    scores["intermittent_fasting"] += 3
            if "特殊节日" in slots:
                scores["festival"] += 2
            if "天气状态" in slots:
                weather = slots["天气状态"]
                if weather in ["寒冷", "阴雨"]:
                    scores["cold_weather_meal_recommendation"] += 2
                elif weather in ["炎热", "晴朗"]:
                    scores["summer_refreshing_meal_recommendation"] += 2

        # 优先级排序
        priority_order = [
            "festival", "game_recommendation",
            "weight_loss", "intermittent_fasting",
            "healthy_diet", "vegetarian",
            "seasonal_food", "child_or_elderly",
            "order"
        ]

        best_intent = max(scores, key=scores.get)
        tied_intents = [intent for intent, score in scores.items() if score == scores[best_intent]]

        if len(tied_intents) > 1:
            for intent in priority_order:
                if intent in tied_intents:
                    return intent

        return best_intent

