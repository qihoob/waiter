from pydantic import BaseModel
from llm_app import build_chain  # 你写的函数
from flask import Flask, jsonify, request
from llm_agent import build_recommend_agent

app = Flask(__name__)


class ChatRequest(BaseModel):
    user_id: str
    restaurant_id: str
    table_id: str
    input_text: str


# 定义一个简单的 API 接口
@app.route("/api/greet", methods=["POST"])
def chat(req: ChatRequest):
    # 构造 session_id，例如 user + 餐厅 + 桌号
    session_id = f"{req.user_id}:{req.restaurant_id}:{req.table_id}"
    # 构建对话链（含记忆）
    chain = build_chain(
        user_id=req.user_id,
        session_id=session_id,
        input_text=req.input_text
    )
    # 执行一次对话
    reply = chain.run(input=req.input_text)

    return {"reply": reply}


# 定义一个简单的 API 接口
@app.route("/api/agent_greet", methods=["POST"])
def chat(req: ChatRequest):
    # 构造 session_id，例如 user + 餐厅 + 桌号
    session_id = f"{req.user_id}:{req.restaurant_id}:{req.table_id}"
    # 构建对话链（含记忆）
    chain = build_recommend_agent(
        user_id=req.user_id,
        session_id=session_id,
        input_text=req.input_text,
        restaurant_id=req.restaurant_id
    )
    # 执行一次对话
    reply = chain.run(input=req.input_text)
    return {"reply": reply}


# 定义 main 函数用于测试
def main():
    # 启动 Flask 开发服务器（仅用于本地测试）
    app.run(debug=True, port=5000)
