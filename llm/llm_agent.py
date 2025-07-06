from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from vector_store.menu_tool import get_menu_tool
from langchain_deepseek import ChatDeepSeek
from memory.redis_memory_manager import RedisMemoryManager
from collector.prompt_builder.prompt import PromptBuilder

# 构建内存管理对象，以获取用户历史对话记录
memory_manager = RedisMemoryManager()
# 构建提示词模板生成器
builder = PromptBuilder(max_length=512)

ds_model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


def build_recommend_agent(user_id, session_id, input_text, restaurant_id):
    tool = get_menu_tool(restaurant_id)
    # 构建上下文
    memory = memory_manager.get_memory(user_id, session_id)
    # 初始化智能体（zero-shot-agent）
    agent = initialize_agent(
        tools=[tool],
        llm=ds_model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )

    # 构建提示词
    prompt = builder.build_prompt(input_text, user_id=user_id, location='location')
    return agent.run(prompt)
