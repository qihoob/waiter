import os
from pathlib import Path
import qrcode

from token_utils import make_token

# ===== 本地开发配置 =====
DOMAIN = os.environ.get("ORDER_ENTRY", "http://127.0.0.1:8000/start")  # 本地指向 FastAPI
SECRET_ENV = os.environ.get("SECRET_KEY")  # 如果没设，会用 token_utils 里的默认
OUTPUT_DIR = Path("./qrcodes")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def make_url(restaurant_id: str, table_id: str) -> str:
    token = make_token(restaurant_id, table_id, ttl_seconds=360000)  # 1小时
    return f"{DOMAIN}?token={token}"

def make_qr(content: str, outfile: Path):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    qr.add_data(content); qr.make(fit=True)
    img = qr.make_image()
    img.save(outfile)

if __name__ == "__main__":
    rid = "r001"
    tid = "T08"
    url = make_url(rid, tid)
    print("签名链接：", url)
    png = OUTPUT_DIR / f"qr_{rid}_{tid}.png"
    make_qr(url, png)
    print("已生成二维码：", png.resolve())

    # 批量示例：
    # for i in range(1, 11):
    #     tid = f"T{str(i).zfill(2)}"
    #     url = make_url(rid, tid)
    #     make_qr(url, OUTPUT_DIR / f"qr_{rid}_{tid}.png")