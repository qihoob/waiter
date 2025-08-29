import time
import uuid

# === 会话管理 ===
_sessions = {}

def _get_session(session_id: str):
    if session_id not in _sessions:
        _sessions[session_id] = {
            "session_id":session_id,
            "restaurant_id": "r001",
            "table_id": "T01",
            "dialog": [],
            "orders": []  # 新增: 保存最终确认的订单
        }
    return _sessions[session_id]