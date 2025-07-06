from langchain.tools import Tool


def send_order(menu: list, user_id: str, table_id):
    import requests
    payload = {
        "userId": user_id,
        "menu": menu,
        "table_id": table_id
    }
    response = requests.post("http://kitchen.api/order", json=payload)
    return f"订单已发送至后厨，响应：{response.text}"


send_order_tool = Tool.from_function(
    func=send_order,
    name="KitchenOrderSender",
    description="将用户已选的菜品发送到后厨系统"
)
