from langchain.agents import Tool
from llm.vector_store.menu_vector_store import get_menu_retriever


def get_menu_tool(restaurant_id: str, query: str):
    retriever = get_menu_retriever(restaurant_id)
    results = retriever.get_relevant_documents(query)
    return "\n".join([doc.page_content for doc in results])


menu_recommend_tool = Tool.from_function(
    name=f"menu_search",
    description="根据用户需求查询当前餐厅的菜单，输出推荐菜品信息",
    func=get_menu_tool
)
