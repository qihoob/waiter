import os, time, uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, Query, HTTPException, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from llm.agent_service import AgentService
from token_utils import verify_and_parse_token

SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME_IN_DEV_ONLY")
FRONTEND_URL = os.environ.get("FRONTEND_URL")  # 可为空；设置后 /start 成功会 302 到它
SESSION_TTL_SECONDS = int(os.environ.get("SESSION_TTL_SECONDS", "7200"))
ALLOW_ORIGINS = os.environ.get("ALLOW_ORIGINS", "*").split(",")

#启动命令
#  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
#测试链接
# http://127.0.0.1:8000/start?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZXN0YXVyYW50X2lkIjoiUjEyMyIsInRhYmxlX2lkIjoiVDA4IiwiaWF0IjoxNzU1ODUyMTE1LCJleHAiOjE3NTU4NTU3MTUsImp0aSI6ImYwOTJjYzNiLTM2NDQtNDM0OS1hMmNhLWM2OTBkNWU3NjFlZSJ9.wl73kDkZ0-uTatfbA2rDKe7HqmIWW9qgcDo6w8TdjzM
# 简单双存储（演示用）
SESSION_STORE: Dict[str, Dict[str, Any]] = {}
JTI_CACHE: Dict[str, int] = {}

app = FastAPI(title="Dining Agent Entry", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
# backend/main.py（只展示需要修改/新增的核心片段）


# 初始化全局单例（也可以按请求注入）
AGENT_SERVICE = AgentService()

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户输入")
    user_id: str | None = None

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    meta: Optional[dict] = None

class VerifyResponse(BaseModel):
    ok: bool
    session_id: Optional[str] = None
    table_id: Optional[str] = None
    restaurant_id: Optional[str] = None
    expire_at: Optional[int] = None

def _new_session(restaurant_id: str, table_id: str, ttl: int = SESSION_TTL_SECONDS) -> dict:
    now = int(time.time())
    session_id = str(uuid.uuid4())
    sess = {
        "session_id": session_id,
        "restaurant_id": restaurant_id,
        "table_id": table_id,
        "created_at": now,
        "expire_at": now + ttl,
        "dialog": [],
    }
    SESSION_STORE[session_id] = sess
    return sess

def _get_session(session_id: str) -> dict:
    sess = SESSION_STORE.get(session_id)
    if not sess:
        raise HTTPException(404, "Session not found")
    if int(time.time()) > sess["expire_at"]:
        SESSION_STORE.pop(session_id, None)
        raise HTTPException(401, "Session expired")
    return sess

@app.get("/healthz")
def healthz():
    return {"ok": True, "ts": int(time.time())}

@app.get("/start")
def start(response: Response, token: str = Query(...)):
    # 验签 + 过期
    try:
        payload = verify_and_parse_token(token)
    except Exception as e:
        raise HTTPException(401, f"Token error: {e}")

    restaurant_id = str(payload.get("restaurant_id"))
    table_id = str(payload.get("table_id"))
    if not restaurant_id or not table_id:
        raise HTTPException(400, "Missing restaurant_id or table_id")

    sess = _new_session(restaurant_id, table_id)

    response.set_cookie(
        "session_id", sess["session_id"], httponly=True, secure=False,  # 本地开发 secure=False
        samesite="Lax", max_age=SESSION_TTL_SECONDS
    )

    if FRONTEND_URL:
        return RedirectResponse(f"{FRONTEND_URL}?session_id={sess['session_id']}", status_code=302)

    return {
        "ok": True,
        "session_id": sess["session_id"],
        "restaurant_id": restaurant_id,
        "table_id": table_id,
        "expire_at": sess["expire_at"],
    }

@app.get("/api/verify", response_model=VerifyResponse)
def api_verify(session_id: str = Query(...)):
    sess = _get_session(session_id)
    return VerifyResponse(
        ok=True, session_id=session_id,
        restaurant_id=sess["restaurant_id"], table_id=sess["table_id"],
        expire_at=sess["expire_at"]
    )

@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest = Body(...)):
    sess = _get_session(req.session_id)

    # 1) 识别 user_id（没有登录就匿名占位）
    user_id = req.user_id or f"anon-{req.session_id}"

    # 2) 存原始对话（可选）
    sess["dialog"].append({"role": "user", "content": req.message, "ts": int(time.time())})

    # 3) 调用你的智能体（把餐厅/桌位/会话上下文一起传进去）
    try:
        reply = AGENT_SERVICE.run(
            user_id=user_id,
            session_id=req.session_id,
            input_text=req.message,
            restaurant_id=sess["restaurant_id"],
            table_id=sess["table_id"],
        )
    except Exception as e:
        # 出错时返回可诊断信息（上线可收敛为统一错误）
        raise HTTPException(500, f"Agent error: {e}")

    # 4) 存 assistant 回复（可选）
    sess["dialog"].append({"role": "assistant", "content": reply, "ts": int(time.time())})

    return ChatResponse(
        session_id=req.session_id,
        reply=reply,
        meta={
            "restaurant_id": sess["restaurant_id"],
            "table_id": sess["table_id"],
            "turns": len(sess["dialog"]),
        },
    )