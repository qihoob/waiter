from pydantic import BaseModel
from llm.llm_agent import build_recommend_agent


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


if __name__ == '__main__':
    qr_data = {
        "table_id": "T15",
        "restaurant_id": "r001",
        "user_id": "13800138000",
        "input_text":"随便来点"
    }
    result = chat(req=qr_data)
    print(result)
