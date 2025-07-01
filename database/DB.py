
def get_user_played_games(user_id):
    """
    根据用户ID查询玩过的游戏
    :param user_id: 用户唯一标识
    :return: 游戏列表
    """
    mock_data = {
        "U123456": ["麻将", "斗地主"],
        "U987654": ["狼人杀", "真心话大冒险"]
    }

    return mock_data.get(user_id, [])

# collector/db/user_profile_db.py

def get_user_order_history(user_id):
    """
    根据用户ID查询历史订单（模拟数据库查询）
    :param user_id: 用户唯一标识
    :return: 历史订单列表
    """
    # 模拟数据库数据，实际应从数据库中查询
    mock_data = {
        "U123456": [
            "水煮鱼",
            "宫保鸡丁",
            "麻婆豆腐",
            "冰可乐 × 2"
        ],
        "U987654": [
            "清蒸鲈鱼",
            "西兰花炒虾仁",
            "南瓜粥",
            "柠檬水"
        ]
    }

    return mock_data.get(user_id, [])
