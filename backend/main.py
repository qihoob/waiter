from fastapi import FastAPI, Query, HTTPException, Response, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field

SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME_IN_DEV_ONLY")
ALLOW_ORIGINS = os.environ.get("ALLOW_ORIGINS", "*").split(",")

app = FastAPI(title="Dining Agent Entry", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
)


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="用户输入")

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

@app.get("/healthz")
def healthz():
    return {"ok": True, "ts": int(time.time())}

@app.get("/start")
def start(response: Response, token: str = Query(...)):
    try:
        payload = verify_and_parse_token(token)
    except Exception as e:
        raise HTTPException(401, f"Token error: {e}")

    restaurant_id = str(payload.get("restaurant_id"))
    table_id = str(payload.get("table_id"))
    if not restaurant_id or not table_id:
        raise HTTPException(400, "Missing restaurant_id or table_id")


    response.set_cookie(
    )

        return RedirectResponse(f"{FRONTEND_URL}?session_id={sess['session_id']}", status_code=302)

@app.get("/api/verify", response_model=VerifyResponse)
def api_verify(session_id: str = Query(...)):
    sess = _get_session(session_id)
    return VerifyResponse(
    )

@app.post("/api/chat", response_model=ChatResponse)
def api_chat(req: ChatRequest = Body(...)):
    sess = _get_session(req.session_id)

    user_id = req.user_id or f"anon-{req.session_id}"


    return ChatResponse(
    )