
from langchain.agents import Tool
from llm.vector_store.menu_vector_store import  get_menu_retriever

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
