SLOT_DICT = {
    "口味": [
        "麻辣", "清淡", "酸甜", "重口味", "不辣", "咸鲜", "香辣", "微辣",
        "清口", "少油", "不要太油腻", "轻一点",  # 淡清别的名
        "辣的", "够劲爆", "四川那种味道", "重口",  # 麻辣别名
        "不辣的", "不能吃辣", "不要放辣", "微辣就行"  # 不辣别名
    ],
    "菜系": [
        "川菜", "湘菜", "粤菜", "东北菜", "日料", "西餐", "本帮菜", "火锅", "烧烤",
        "四川菜", "辣子多",  # 川菜别名
        "湖南菜", "辣得狠",  # 湘菜别名
        "广东菜", "广府菜",  # 粤菜别名
        "北方菜", "大锅炖", "家常菜",  # 东北菜别名
        "寿司", "刺身", "日本料理",  # 日料理别名
        "牛排", "意面", "洋餐",  # 西餐别名
        "涮锅", "麻辣烫", "热锅",  # 火锅别名
        "烤串", "撸串", "BBQ"  # 烧烤别名
    ],
    "饮品": [
        "啤酒", "果汁", "奶茶", "红酒", "白酒", "可乐", "咖啡", "气泡水",
        "啤的", "喝两瓶啤", "来点冰的",  # 啤酒别名
        "高度酒", "烧喉", "一口闷",  # 白酒别名
        "奶盖", "芝士奶盖", "茶饮",  # 奶茶别名
        "鲜榨", "果茶", "水果汁"  # 果汁别名
    ],
    "游戏": [
        "麻将", "斗地主", "狼人杀", "你画我猜", "谁是卧底", "拼图游戏"
    ],
    "场景": [
        "朋友聚会", "公司年会", "家庭聚餐", "情侣约会", "生日宴", "商务宴请",
        "大家一块儿吃", "朋友一起玩", "多人聚餐", "聚餐",  # 朋友聚会别名
        "二人世界", "小两口吃饭", "约会吃饭",  # 情侣约会别名
        "带娃吃饭", "一家老小聚餐", "家庭聚会", "亲子聚餐", "亲子活动", "一家小聚", "家庭餐"  # 家庭聚餐别名
    ],
    "就餐环境": [
        "有包间", "安静", "适合聊天", "亲子环境", "环境优雅", "有音乐", "正式"
    ],
    "就餐形式": [
        "桌餐", "围炉", "自助餐", "火锅", "烧烤", "快餐",
        "围炉煮茶", "炭火煮茶", "围炉夜话",  # 围炉别名
        "随便拿", "想吃多少拿多少", "任吃"  # 自助餐别名
    ],
    "健康偏好": [
        "低脂", "高蛋白", "无糖", "清淡",
        "少油少盐", "减肥餐", "轻食",  # 低脂别名
        "不加糖", "少糖", "控糖"  # 无糖别名
    ],
    "特殊节日": [
        "情人节", "七夕", "圣诞节", "元旦"
    ],
    "天气状态": [
        "寒冷", "炎热", "阴雨", "晴朗"
    ],
    "忌口": [
        "不吃辣", "忌海鲜",
        "怕辣", "不太能吃辣", "辣的不行",  # 不吃辣别名
        "不吃鱼虾", "海鲜过敏", "甲壳类不要"  # 忌海鲜别名
    ],
    "过敏原": [
        "花生", "牛奶", "海鲜",
        "坚果", "nuts", "花仁",  # 花生别名
        "乳制品", "奶制品", "dairy"  # 牛奶别名
    ]
}

# 新增：地方特色菜品映射（可用于推荐）
LOCAL_SPECIALTY = {
    "北京": ["涮羊肉", "炸酱面", "卤煮"],
    "上海": ["生煎包", "蟹粉小笼", "腌笃鲜"],
    "广州": ["早茶", "白切鸡", "肠粉"],
    "成都": ["火锅", "冒菜", "钟水饺"],
    "长沙": ["剁椒鱼头", "臭豆腐", "口味虾"],
    "西安": ["肉夹馍", "凉皮", "羊肉泡馍"],
    "重庆": ["麻辣火锅", "毛血旺", "串串香"],
    "杭州": ["东坡肉", "西湖醋鱼", "龙井虾仁"],
    "武汉": ["热干面", "豆皮", "鸭脖"],
    "哈尔滨": ["锅包肉", "红肠", "俄式西餐"],
    "深圳": ["港式茶餐厅", "潮汕牛肉火锅", "新派融合菜"],
}


GAME_RECOMMENDATION_RULES = {
    "朋友聚会": ["麻将", "斗地主", "狼人杀"],
    "情侣约会": ["你画我猜", "真心话大冒险", "默契挑战"],
    "家庭聚餐": ["拼图游戏", "亲子互动游戏", "谁是卧底"],
    "公司年会": ["桌游+角色扮演", "团队推理", "卡牌竞技"],
    "商务宴请": ["轻松聊天类游戏", "背景音乐氛围互动"]
}

GAME_ENVIRONMENT_MAP = {
    "有包间": ["麻将", "狼人杀", "拼图游戏"],
    "适合聊天": ["你画我猜", "谁是卧底", "真心话大冒险"],
    "正式": ["轻节奏桌游", "推理类", "策略型"],
    "安静": ["拼图游戏", "卡牌类", "手机App小游戏"]
}
ORDER_KEYWORDS = [
    "下单", "点菜", "订位", "订桌", "订好了", "订过", "订座", "订餐",
    "点了", "选好了", "确定了", "已经订", "准备点菜"
]

ORDER_ALIAS_MAP = {
    "下单": ["点菜", "订位", "订桌", "订座", "订餐"],
    "已下单": ["订好了", "订过", "确定了", "已经订"]
}

INTENT_TO_TEMPLATE_MAP = {
    "order": "enhanced_basic_with_all",
    "game_recommendation": "pre_meal_game_recommendation",
    "healthy_diet": "healthy_diet_recommendation",
    "festival": "festival_special_meal_recommendation",
    "vegetarian": "vegetarian_meal_recommendation",
    "weather_based": "cold_weather_meal_recommendation",  # 动态切换冬夏
    "child_or_elderly": "child_or_elderly_health_meal",
    "weight_loss": "weight_loss_meal_recommendation",
    "intermittent_fasting": "intermittent_fasting_or_low_sugar_meal",
    "seasonal_food": "cold_weather_meal_recommendation",  # 动态判断
    "fitness_nutrition": "weight_loss_meal_recommendation",  # 可复用
    "holiday_event": "festival_special_meal_recommendation",
    "group_gathering": "enhanced_basic_with_all",
    "takeaway_service": "summer_refreshing_meal_recommendation",
    "allergy_safe": "healthy_diet_recommendation",
    "nutritional_info": "weight_loss_meal_recommendation"
}

TEMPLATE_TYPES = {
    "enhanced_basic_with_all": "base",
    "pre_meal_game_recommendation": "action",
    "healthy_diet_recommendation": "intent",
    "festival_special_meal_recommendation": "contextual",
    "vegetarian_meal_recommendation": "intent",
    "child_or_elderly_health_meal": "intent",
    "cold_weather_meal_recommendation": "contextual",
    "summer_refreshing_meal_recommendation": "contextual",
    "weight_loss_meal_recommendation": "intent",
    "intermittent_fasting_or_low_sugar_meal": "intent"
}


INTENT_KEYWORDS = {
    "order": ["点餐", "下单", "我要吃", "来一份"],
    "game_recommendation": ["玩什么", "游戏", "饭前玩", "娱乐"],
    "healthy_diet": ["健康", "清淡", "少油", "少盐"],
    "vegetarian": ["素食", "不吃肉", "素菜", "清真"],
    "weight_loss": ["减肥", "减脂", "低卡", "瘦身"],
    "intermittent_fasting": ["断食", "控糖", "无糖"],
    "child_or_elderly": ["儿童", "老人", "小孩", "长者"],
    "festival": ["节日", "圣诞", "春节", "情人节"],
    "seasonal_food": ["夏天", "冬天", "冷饮", "热汤"],
    "fitness_nutrition": ["蛋白", "健身", "增肌"],
    "takeaway_service": ["外卖", "打包", "带走"],
    "allergy_safe": ["过敏", "花生", "牛奶", "海鲜"],
    "nutritional_info": ["热量", "营养", "卡路里"]
}

KEYWORD_WEIGHT_RULES = {
    "weight_loss": {
        "关键词": [
            "低脂", "减肥", "少油", "轻食", "清淡", "减脂", "控卡",
            "瘦身", "轻一点", "不要太油腻"
        ],
        "位置权重": {"ATT": 0.4, "OBJ": 0.3, "ADV": 0.2},
    },
    "pre_meal_game": {
        "关键词": ["游戏", "玩什么", "麻将", "桌游", "娱乐", "饭前玩"],
        "位置权重": {"OBJ": 0.5, "ADV": 0.3},
    },
    "vegetarian": {
        "关键词": ["素食", "不吃肉", "清真", "素菜", "不吃荤"],
        "位置权重": {"OBJ": 0.5, "ADV": 0.3}
    },
    "healthy_diet": {
        "关键词": ["健康", "清淡", "少油", "少盐", "养生", "养胃", "营养"],
        "位置权重": {"ATT": 0.35, "OBJ": 0.25, "ADV": 0.15}
    },
    "spicy_food": {
        "关键词": ["麻辣", "辣的", "重口味", "够劲爆", "四川那种味道"],
        "位置权重": {"ATT": 0.4, "OBJ": 0.3, "ADV": 0.2}
    },
    "sweet_food": {
        "关键词": ["甜", "酸甜", "糖醋", "蜜汁", "带点甜味"],
        "位置权重": {"OBJ": 0.3, "ATT": 0.25, "ADV": 0.15}
    },
    "sichuan_cuisine": {
        "关键词": ["川菜", "四川菜", "辣子多", "麻辣香锅", "水煮鱼"],
        "位置权重": {"OBJ": 0.4, "ATT": 0.3, "ADV": 0.2}
    },
    "cantonese_cuisine": {
        "关键词": ["粤菜", "广东菜", "广府菜", "早茶", "烧味"],
        "位置权重": {"OBJ": 0.4, "ATT": 0.3, "ADV": 0.2}
    },
    "japanese_cuisine": {
        "关键词": ["日料", "寿司", "刺身", "日本料理", "拉面"],
        "位置权重": {"OBJ": 0.4, "ATT": 0.3, "ADV": 0.2}
    },
    "western_cuisine": {
        "关键词": ["西餐", "牛排", "意面", "洋餐", "披萨"],
        "位置权重": {"OBJ": 0.4, "ATT": 0.3, "ADV": 0.2}
    },
    "hotpot": {
        "关键词": ["火锅", "涮锅", "麻辣烫", "热锅"],
        "位置权重": {"OBJ": 0.4, "ATT": 0.3, "ADV": 0.2}
    },
    "bbq": {
        "关键词": ["烧烤", "烤串", "撸串", "BBQ"],
        "位置权重": {"OBJ": 0.4, "ATT": 0.3, "ADV": 0.2}
    },
    "beverage": {
        "关键词": ["啤酒", "果汁", "奶茶", "红酒", "白酒", "可乐", "咖啡", "气泡水"],
        "位置权重": {"OBJ": 0.4, "ATT": 0.3, "ADV": 0.2}
    },
    "game_recommendation": {
        "关键词": ["麻将", "斗地主", "狼人杀", "你画我猜", "谁是卧底", "拼图游戏"],
        "位置权重": {"OBJ": 0.5, "ADV": 0.3}
    },
    "scene_recommendation": {
        "关键词": ["朋友聚会", "公司年会", "家庭聚餐", "情侣约会", "生日宴", "商务宴请"],
        "位置权重": {"OBJ": 0.5, "ADV": 0.3}
    },
    "dining_environment": {
        "关键词": ["有包间", "安静", "适合聊天", "亲子环境", "环境优雅", "有音乐", "正式"],
        "位置权重": {"OBJ": 0.5, "ADV": 0.3}
    },
    "dining_style": {
        "关键词": ["桌餐", "围炉", "自助餐", "火锅", "烧烤", "快餐"],
        "位置权重": {"OBJ": 0.5, "ADV": 0.3}
    },
    "health_preference": {
        "关键词": ["低脂", "高蛋白", "无糖", "清淡", "少油少盐", "减肥餐", "轻食"],
        "位置权重": {"OBJ": 0.4, "ATT": 0.3, "ADV": 0.2}
    },
    "special_event": {
        "关键词": ["情人节", "七夕", "圣诞节", "元旦"],
        "位置权重": {"OBJ": 0.5, "ADV": 0.3}
    }
}

