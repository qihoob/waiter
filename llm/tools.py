import uuid
import json
from typing import Dict, List
from langchain.agents import Tool

from utils.session_manager import _get_session


# === 工具函数 ===
def get_menu_tool(query: str):
    print("调用get_menu_tool工具")
    sample_menu = [
        {"id": "d001", "name": "北京烤鸭", "price": 198},
        {"id": "d002", "name": "炸酱面", "price": 28},
        {"id": "d003", "name": "豆汁", "price": 12},
        {"id": "d004", "name": "卤煮火烧", "price": 32}
    ]
    return "\n".join([f"{d['name']} - {d['price']}元" for d in sample_menu])


def confirm_order_checker_tool(selected_items: List[Dict], existing_items: List[Dict]) -> List[Dict]:
    print("调用confirm_order_checker_tool工具")
    confirmed_items = {item["id"]: item for item in existing_items}
    for item in selected_items:
        if item["id"] in confirmed_items:
            confirmed_items[item["id"]]["quantity"] += item.get("quantity", 1)
        else:
            confirmed_items[item["id"]] = {
                "id": item["id"],
                "name": item["name"],
                "price": item["price"],
                "quantity": item.get("quantity", 1)
            }
    return list(confirmed_items.values())


def send_order_tool(order: Dict) -> str:
    print(">>> 发送到后厨系统:", order)
    return f"订单 {order.get('order_id', '未知')} 已发送给后厨"


def process_order_tool(llm_output: str, session_id: str = None) -> str:
    """
    处理 LLM 输出生成的订单:
    1. 解析 LLM 输出 (JSON 格式)
    2. 合并已有订单与新订单
    3. 调用确认工具 confirm_order_checker_tool 过滤和确认菜品
    4. 生成订单 ID 并保存到 session
    5. 调用 send_order_tool 模拟下单
    6. 返回自然语言结果，避免循环调用
    """
    print("调用 process_order_tool 工具")

    try:
        # Step 1: 解析 LLM 输出
        try:
            data = json.loads(llm_output)
        except json.JSONDecodeError:
            return "订单处理失败：LLM 输出格式错误，无法解析 JSON"

        order_items = data.get("order", [])
        reply_text = data.get("reply", "")
        if not isinstance(order_items, list):
            return "订单处理失败：解析出的 'order' 字段不是列表"

        if not order_items:
            return "用户未选择菜品，无法下单"

        # Step 2: 获取已有订单（若 session_id 存在）
        existing_items: List[Dict[str, Any]] = []
        sess = None
        if session_id:
            sess = _get_session(session_id)
            if sess and "orders" in sess and sess["orders"]:
                existing_items = sess["orders"][-1].get("order", [])

        # Step 3: 确认和合并订单
        confirmed_items = confirm_order_checker_tool(order_items, existing_items)
        if not confirmed_items:
            return "订单处理失败：未确认到有效菜品"

        # Step 4: 生成订单字典
        order_dict = {
            "order_id": str(uuid.uuid4()),
            "order": confirmed_items
        }

        # Step 5: 保存到 session
        if sess is not None:
            sess.setdefault("orders", []).append(order_dict)

        # Step 6: 调用 send_order_tool 模拟下单
        send_order_tool(order_dict)

        # Step 7: 生成自然语言确认结果（避免再被当成 Action）
        items_desc = "，".join([f"{i['quantity']}份{i['name']}" for i in confirmed_items])
        return f"{reply_text}\n（订单号：{order_dict['order_id']}，包含菜品：{items_desc}）"

    except Exception as e:
        return f"订单处理失败: {str(e)}"


menu_recommend_tool = Tool.from_function(
    name="menu_search",
    func=get_menu_tool,
    description="根据用户需求查询当前餐厅菜单，输出推荐菜品信息"
)

process_order_tool_wrapper = Tool.from_function(
    name="process_order_tool",
    func=lambda x: process_order_tool(x, None),
    description="解析 LLM 输出 JSON 并发送订单到后厨"
)
