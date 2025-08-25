import base64, hashlib, hmac, json, time, uuid, os

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    # 允许生成脚本里直接设置，也可以在环境变量里设置
    SECRET_KEY = "CHANGE_ME_IN_DEV_ONLY"

def _b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def _b64url_decode_nopad(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)

def sign_token(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h64 = _b64url_encode(json.dumps(header, separators=(",", ":"), ensure_ascii=False).encode())
    p64 = _b64url_encode(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode())
    signing_input = f"{h64}.{p64}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    s64 = _b64url_encode(signature)
    return f"{h64}.{p64}.{s64}"

def make_token(restaurant_id: str, table_id: str, ttl_seconds: int = 3600) -> str:
    now = int(time.time())
    payload = {
        "restaurant_id": restaurant_id,
        "table_id": table_id,
        "iat": now,
        "exp": now + ttl_seconds,
        "jti": str(uuid.uuid4()),
    }
    return sign_token(payload)

def verify_and_parse_token(token: str) -> dict:
    try:
        h64, p64, s64 = token.split(".")
    except ValueError:
        raise ValueError("Malformed token")

    signing_input = f"{h64}.{p64}".encode()
    expected = hmac.new(SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    given = _b64url_decode_nopad(s64)
    if not hmac.compare_digest(expected, given):
        raise ValueError("Invalid signature")

    payload = json.loads(_b64url_decode_nopad(p64).decode())
    now = int(time.time())
    if now > int(payload.get("exp", 0)):
        raise ValueError("Token expired")
    return payload