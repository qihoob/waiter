from langchain.agents import initialize_agent, AgentType
from langchain_deepseek import ChatDeepSeek

from llm.tools import menu_recommend_tool, process_order_tool, process_order_tool_wrapper
from llm.prompt_builder import PromptBuilder
from memory.redis_memory_manager import RedisMemoryManager

# === Agent Service ===
class AgentService:
    def __init__(self):
        self.memory_manager = RedisMemoryManager()
        self.prompt_builder = PromptBuilder()
        self.repo = {
            "r001": {
                "name": "京味轩",
                "location": "北京",
                "opening_hours": "10:00-22:00"
            }
        }
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        self.tools = [menu_recommend_tool, process_order_tool_wrapper]

    def get_restaurant_profile(self, restaurant_id: str):
        return self.repo.get(restaurant_id, {"name": "未知餐厅", "location": "未知", "opening_hours": "未知"})

    def run(self, user_id: str, session_id: str, input_text: str, restaurant_id: str,
            table_id: str = None) -> str:
        memory = self.memory_manager.get_memory(user_id, session_id)
        dialog_history = "\n".join([f"{m.type}: {m.content}" for m in memory.chat_memory.messages])
        restaurant = self.get_restaurant_profile(restaurant_id)
        final_prompt = self.prompt_builder.build_prompt(
            restaurant=restaurant,
            dialog_history=dialog_history,
            user_input=input_text,
            scene_type="独自吃饭",
            num_people="1",
            taste_pref="清淡",
            table_id=table_id or "未知"
        )
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True  # 🔑 加这一行
        )
        # 给 process_order_tool 传递 session_id
        self.tools[1].func = lambda x: process_order_tool(x, session_id)
        reply = agent.run(final_prompt)
        memory.save_context({"input": input_text}, {"output": reply})
        return reply
