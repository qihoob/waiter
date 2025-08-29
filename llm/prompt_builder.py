from typing import Dict, Any
from langchain.prompts import PromptTemplate

# === Prompt Builder ===
class PromptBuilder:
    def __init__(self):
        self.template = """
你是一个智能服务员，需要完成以下任务：
- 理解用户需求
- 提供餐厅服务
- 推荐本地特色菜品
- 协助处理点单和投诉
【餐厅信息】
餐厅名称: {restaurant_name}
所在城市: {location}
营业时间: {opening_hours}
桌号: {table_id}
【历史对话】（按时间顺序）
{dialog_history}
【当前用户请求】
{user_input}
【用户画像】
场景类型: {scene_type}
参与人数: {num_people}
口味偏好: {taste_pref}
请基于以上信息，完成以下任务：
1. 用{location}地方特色的口吻先进行简短、贴心的服务回复
2. 输出最终订单，严格使用以下 JSON 格式：
{{
  "reply": "自然语言回答给用户",
  "order": [{{"id": "菜品ID","name":"菜品名称","price":价格, "quantity": 数量}}]
}}
⚠️ 重要约束：
- 在用户“确认并下单”之前，绝不要生成订单号。
- 每次输出时，order 字段必须包含用户已推荐或已选择的所有菜品。
- 如果用户只是加菜，不要丢失之前推荐或已选的菜品，要合并展示。
- 当用户说“确认并下单”时：
  1. 只调用一次 `process_order_tool` 工具；
  2. 之后必须结束思考，直接输出自然语言确认结果；
  3. 不要再次调用任何工具。
"""
        self.prompt_template = PromptTemplate(
            input_variables=[
                "restaurant_name", "location", "opening_hours", "table_id",
                "dialog_history", "user_input", "scene_type", "num_people", "taste_pref"
            ],
            template=self.template
        )

    def build_prompt(
            self,
            restaurant: Dict[str, Any],
            dialog_history: str,
            user_input: str,
            scene_type: str = "未知",
            num_people: str = "未知",
            taste_pref: str = "无",
            table_id: str = "未知",
    ) -> str:
        return self.prompt_template.format(
            restaurant_name=restaurant.get("name", "未知餐厅"),
            location=restaurant.get("location", "未知地区"),
            opening_hours=restaurant.get("opening_hours", "未知"),
            table_id=table_id,
            dialog_history=dialog_history or "暂无历史记录",
            user_input=user_input,
            scene_type=scene_type,
            num_people=num_people,
            taste_pref=taste_pref,
        )