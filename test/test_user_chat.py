from llm import build_recommend_agent
import re

def chat(req):
    # 构造 session_id，例如 user + 餐厅 + 桌号
    session_id = f"{req['user_id']}:{req['restaurant_id']}:{req['table_id']}"
    # 构建对话链（含记忆）
    reply = build_recommend_agent(
        user_id=req['user_id'],
        session_id=session_id,
        input_text=req['input_text'],
        restaurant_id=req['restaurant_id']
    )
    # 执行一次对话
    return {"reply": reply}

# 提取菜品
# 提取菜品信息
def extract_dishes_from_reply(reply_text):
    pattern = r"\d+\.\s*(.+?)\s*-\s*"
    return re.findall(pattern, reply_text)


# 生成确认菜单文本
def generate_menu_confirmation(dish_list, dialect='sichuan'):
    if dialect == 'sichuan':
        header = "菜单整好啦客官，请瞅哈：\n"
        footer = "\n要是觉得安逸，我这就给您安排下单哈～"
    elif dialect == 'shanghai':
        header = "菜单配好啦阿拉客人，请看看：\n"
        footer = "\n伐错的话，我就帮侬安排了噢～"
    else:
        header = "菜单如下，请确认：\n"
        footer = "\n如无问题，将为您下单～"

    menu_lines = [f"- {dish}" for dish in dish_list]
    return header + "\n".join(menu_lines) + footer

if __name__ == '__main__':
    qr_data = {
        "table_id": "T15",
        "restaurant_id": "r001",
        "user_id": "13800138000",
        "input_text":"随便来点"
    }
    result = chat(req=qr_data)
    print(result)

    reply_text = result["reply"]
    dishes = extract_dishes_from_reply(reply_text)
    confirmation_text = generate_menu_confirmation(dishes, dialect="sichuan")
    print(confirmation_text)
