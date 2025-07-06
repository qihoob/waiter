from langchain.vectorstores import Chroma
from langchain.schema import Document
from langchain.agents import Tool
from langchain_huggingface import HuggingFaceEmbeddings

# 推荐使用中文优化的 BGE 模型（Better General Embedding）
embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh")


def build_menu_vector_store(restaurant_id: str, menu_items: list[dict]):
    # 1. 构建 Document 列表
    docs = []
    for item in menu_items:
        content = (
            f"{item['name']}：{item['description']}。价格：{item['price']}元。"
            f"标签：{'、'.join(item['tags'])}。"
            f"适合：{'、'.join(item['suitable_for'])}。"
            f"健康建议：{'、'.join(item['health_info'])}。"
            f"推荐时间：{item['best_serving_time']}。"
        )
        docs.append(Document(page_content=content, metadata={"restaurant_id": restaurant_id}))

    # 2. 向量存储路径（每个餐厅单独）
    persist_dir = f"./vector_store/{restaurant_id}"

    # 3. 构建 Chroma 向量库
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=persist_dir
    )
    vectordb.persist()
    return vectordb


def get_menu_retriever(restaurant_id: str):
    persist_dir = f"./vector_store/{restaurant_id}"
    vectordb = Chroma(
        persist_directory=persist_dir,
        embedding_function=embedding_model
    )
    return vectordb.as_retriever()


def get_menu_tool(restaurant_id: str):
    retriever = get_menu_retriever(restaurant_id)

    def search_menu(query: str):
        results = retriever.get_relevant_documents(query)
        return "\n".join([doc.page_content for doc in results])

    return Tool.from_function(
        name=f"menu_search_{restaurant_id}",
        description="根据用户需求查询当前餐厅的菜单，输出推荐菜品信息",
        func=search_menu
    )
