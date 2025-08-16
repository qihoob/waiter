# slot_definitions.py
from typing import Dict, Set, List

# 定义所有支持的槽位
SLOT_DEFINITIONS = {
    # 基础用户信息
    "人数": {
        "type": "numeric",
        "description": "用餐人数",
        "examples": ["1人", "三个人", "4位"]
    },
    "场景": {
        "type": "categorical",
        "description": "用餐场景",
        "examples": ["朋友聚会", "家庭聚餐", "商务宴请", "约会"]
    },
    "城市": {
        "type": "location",
        "description": "用户所在城市",
        "examples": ["北京", "上海", "广州"]
    },
    "地区": {
        "type": "location",
        "description": "用户所在地区",
        "examples": ["海淀区", "浦东新区"]
    },

    # 餐饮相关
    "菜系": {
        "type": "categorical",
        "description": "菜系偏好",
        "examples": ["川菜", "粤菜", "日料", "西餐"]
    },
    "口味": {
        "type": "categorical",
        "description": "口味偏好",
        "examples": ["辣味", "清淡", "酸甜", "咸鲜"]
    },
    "饮品": {
        "type": "categorical",
        "description": "饮品偏好",
        "examples": ["可乐", "啤酒", "茶", "咖啡"]
    },
    "就餐环境": {
        "type": "categorical",
        "description": "就餐环境要求",
        "examples": ["安静", "热闹", "浪漫"]
    },
    "就餐形式": {
        "type": "categorical",
        "description": "就餐形式",
        "examples": ["堂食", "外卖", "打包"]
    },
    "特色菜": {
        "type": "text",
        "description": "特色菜品",
        "examples": ["麻婆豆腐", "北京烤鸭"]
    },
    "家常菜": {
        "type": "text",
        "description": "家常菜品",
        "examples": ["番茄炒蛋", "红烧肉"]
    },
    "核心口味": {
        "type": "categorical",
        "description": "核心口味",
        "examples": ["麻辣", "酸甜", "鲜咸"]
    },
    "味型细分": {
        "type": "categorical",
        "description": "味型细分",
        "examples": ["微辣", "重辣", "清淡"]
    },
    "菜系说明": {
        "type": "text",
        "description": "菜系说明"
    },
    "口味特点": {
        "type": "text",
        "description": "口味特点描述"
    },
    "预算": {
        "type": "numeric",
        "description": "预算范围",
        "examples": ["100元", "200左右"]
    },

    # 健康相关
    "健康偏好": {
        "type": "categorical",
        "description": "健康偏好",
        "examples": ["低脂", "高蛋白", "无糖", "减肥餐"]
    },
    "忌口": {
        "type": "list",
        "description": "忌口食物",
        "examples": ["辣椒", "花生", "海鲜"]
    },
    "过敏原": {
        "type": "list",
        "description": "过敏原",
        "examples": ["海鲜", "坚果", "乳制品"]
    },

    # 环境相关
    "天气": {
        "type": "categorical",
        "description": "天气状况",
        "examples": ["晴天", "雨天", "雪天"]
    },
    "节日": {
        "type": "categorical",
        "description": "节日信息",
        "examples": ["春节", "情人节", "圣诞节"]
    },
    "节日信息": {
        "type": "dict",
        "description": "节日详细信息"
    },

    # 游戏相关
    "游戏": {
        "type": "categorical",
        "description": "游戏偏好",
        "examples": ["狼人杀", "剧本杀", "桌游"]
    },

    # 其他
    "订单状态": {
        "type": "categorical",
        "description": "订单状态信息",
        "examples": ["下单意图", "已订好"]
    }
}

# 意图与必需槽位的映射关系
INTENT_REQUIRED_SLOTS = {
    # 餐饮相关意图
    "order_food": {"菜系", "人数", "场景", "口味", "健康偏好"},
    "recommend_dish": {"菜系", "人数", "场景", "口味", "健康偏好"},
    "query_nutrition": {"健康偏好", "忌口", "过敏原"},

    # 游戏相关意图
    "recommend_game": {"场景", "人数", "游戏"},
    "play_game": {"游戏", "人数"},

    # 饮品相关意图
    "order_drink": {"饮品", "人数"},
    "recommend_drink": {"饮品", "场景"},

    # 节日相关意图
    "festival_recommend": {"节日", "场景", "人数"},

    # 默认意图需要的槽位
    "default": {"场景", "人数"},
    "enhanced_basic_with_all": {"菜系", "人数", "场景", "口味", "健康偏好"}
}

# 槽位处理器映射
SLOT_HANDLER_MAPPING = {
    "人数": "PeopleCountSlotHandler",
    "场景": "SceneSlotHandler",
    "城市": "LocationSlotHandler",
    "菜系": "CuisineFlavorHandler",
    "口味": "TasteSlotHandler",
    "饮品": "DrinkSlotHandler",
    "健康偏好": "HealthPreferenceSlotHandler",
    "忌口": "DietaryRestrictionSlotHandler",
    "过敏原": "AllergenSlotHandler",
    "天气": "WeatherSlotHandler",
    "节日": "FestivalSlotHandler",
    "游戏": "GameSlotHandler"
}
