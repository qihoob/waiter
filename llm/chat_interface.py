import uuid
import time
from llm.agent_service import AgentService
from utils.session_manager import _get_session

# === 对话接口 ===
AGENT_SERVICE = AgentService()

def chat_with_agent(message: str, session_id: str = None, user_id: str = None):
    if not session_id:
        session_id = str(uuid.uuid4())
    sess = _get_session(session_id)
    user_id = user_id or f"anon-{session_id}"
    sess["dialog"].append({"role": "user", "content": message, "ts": int(time.time())})
    try:
        reply = AGENT_SERVICE.run(
            user_id=user_id,
            session_id=session_id,
            input_text=message,
            restaurant_id=sess["restaurant_id"],
            table_id=sess["table_id"]
        )
    except Exception as e:
        reply = f"[Agent Error] {e}"
    sess["dialog"].append({"role": "assistant", "content": reply, "ts": int(time.time())})
    return {
        "session_id": session_id,
        "reply": reply,
        "meta": {
            "restaurant_id": sess["restaurant_id"],
            "table_id": sess["table_id"],
            "turns": len(sess["dialog"]),
            "orders": sess["orders"]
        },
        "dialog": sess["dialog"]
    }
