# collector/mcp/weather_client.py

import random

def get_weather_by_location(location):
    """
    根据地点获取当前天气情况（模拟 API 调用）
    :param location: 地点名称（如“北京”、“成都”）
    :return: 包含天气和温度的字典
    """
    # 模拟不同城市的天气数据
    weather_mapping = {
        "北京": {"weather": "晴朗", "temperature": 25},
        "上海": {"weather": "多云", "temperature": 28},
        "广州": {"weather": "炎热", "temperature": 34},
        "成都": {"weather": "阴天", "temperature": 22},
        "哈尔滨": {"weather": "寒冷", "temperature": -5},
        "深圳": {"weather": "雷阵雨", "temperature": 30}
    }

    return weather_mapping.get(location, {"weather": "未知", "temperature": 20})
