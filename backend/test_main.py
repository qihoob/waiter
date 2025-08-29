import uuid
import time
from llm.chat_interface import chat_with_agent


if __name__ == "__main__":
    session_id = str(uuid.uuid4())
    res1 = chat_with_agent(message="推荐几个北京传统特色菜", session_id=session_id)
    print("Assistant:", res1["reply"])
    res2 = chat_with_agent(message="可以，再加一份北京烤鸭", session_id=session_id)
    print("Assistant:", res2["reply"])
    res3 = chat_with_agent(message="确认并下单", session_id=session_id)
    print("Assistant:", res3["reply"])

    print("\n=== 历史对话 ===")
    for turn in res3["dialog"]:
        print(f"{turn['role']}: {turn['content']}")

    print("\n=== 确认的订单 ===")
    print(res3["meta"]["orders"])