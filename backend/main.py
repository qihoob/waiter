# waiter/backend/main.py
import os
import time
import uuid
from typing import Optional
from fastapi import FastAPI, Query, HTTPException, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from llm.chat_interface import chat_with_agent
from utils.session_manager import _get_session  # 使用 session_manager.py
from backend.token_utils import verify_and_parse_token

# ================== 配置 ==================
SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME_IN_DEV_ONLY")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://127.0.0.1:8000/static/chat.html")
ALLOW_ORIGINS = os.environ.get("ALLOW_ORIGINS", "*").split(",")
SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS", "7200"))

# ================== FastAPI 初始化 ==================
app = FastAPI(title="Dining Agent Entry", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ================== 数据模型 ==================
class ChatRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户输入")
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    meta: Optional[dict] = None
    dialog: Optional[list] = None

class VerifyResponse(BaseModel):
    ok: bool
    session_id: Optional[str] = None
    table_id: Optional[str] = None
    restaurant_id: Optional[str] = None
    expire_at: Optional[int] = None

# ================== 路由 ==================
@app.get("/healthz")
def healthz():
    return {"ok": True, "ts": int(time.time())}

@app.get("/start")
def start(response: Response, token: str = Query(...)):
    """
    1. 验证 token
    2. 创建会话
    3. 返回前端 chat.html
    """
    try:
        payload = verify_and_parse_token(token)
    except Exception as e:
        raise HTTPException(401, f"Token error: {e}")

    restaurant_id = str(payload.get("restaurant_id"))
    table_id = str(payload.get("table_id"))
    if not restaurant_id or not table_id:
        raise HTTPException(400, "Missing restaurant_id or table_id")

    # 使用 _get_session 创建会话，如果不存在会自动创建
    sess = _get_session(str(uuid.uuid4()))
    sess["restaurant_id"] = restaurant_id
    sess["table_id"] = table_id
    sess["created_at"] = int(time.time())
    sess["expire_at"] = sess["created_at"] + SESSION_TTL_SECONDS

    response.set_cookie(
        "session_id",
        sess["session_id"],
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=SESSION_TTL_SECONDS,
    )

    # 跳转到前端 chat.html
    return RedirectResponse(f"{FRONTEND_URL}?session_id={sess['session_id']}", status_code=302)

@app.get("/api/verify", response_model=VerifyResponse)
def api_verify(session_id: str = Query(...)):
    sess = _get_session(session_id)
    now = int(time.time())
    if now > sess.get("expire_at", 0):
        raise HTTPException(401, "Session expired")
    return VerifyResponse(
        ok=True,
        session_id=session_id,
        restaurant_id=sess["restaurant_id"],
        table_id=sess["table_id"],
        expire_at=sess["expire_at"],
    )

@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest = Body(...)):
    """
    前端每次输入都会调用此接口。
    通过 chat_with_agent 完成对话并返回助手回复和会话信息。
    """
    sess = _get_session(req.session_id)
    now = int(time.time())
    if now > sess.get("expire_at", 0):
        raise HTTPException(401, "Session expired")

    user_id = req.user_id or f"anon-{req.session_id}"

    # 调用智能体对话接口
    res = chat_with_agent(message=req.message, session_id=req.session_id, user_id=user_id)

    return ChatResponse(
        session_id=res["session_id"],
        reply=res["reply"],
        meta=res["meta"],
        dialog=res["dialog"]
    )

@app.get("/")
def read_root():
    return {"Hello": "World"}

# ================== 启动 ==================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
