from schema import PromptContext

# 模拟上下文获取
def get_user_context(user_id: str) -> PromptContext:
    return PromptContext(
        user_id=user_id,
        time="晚餐",
        weather="阴天",
        location="广州",
        history=["麻辣香锅", "水煮鱼", "青岛啤酒"]
    )
