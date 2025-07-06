import json
from llm.vector_store.menu_vector_store import *


def init_vector_stor():
    with open("D:/PycharmProjects/waiter/database/restaurant_menu_enriched.json", "r", encoding="utf-8") as f:
        menu_data = json.load(f)
    restaurant_id = menu_data["restaurant_id"]
    menu_items = menu_data["menu"]
    build_menu_vector_store(restaurant_id, menu_items)


def test_search(query):
    # 检索与 query 最相关的前 5 道菜
    # 用户自然语言查询内容
    retriever = get_menu_retriever(restaurant_id='r001')
    results = retriever.get_relevant_documents(query)
    # 输出结果
    for i, doc in enumerate(results, 1):
        print(f"\n🔍 推荐第{i}道菜：")
        print(doc.page_content)


if __name__ == '__main__':
    # 初始化一次
    # init_vector_stor()
    test_search(query='约会，推荐两道菜')
