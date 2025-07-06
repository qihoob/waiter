from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType

from llm.tool.call_kitchen_api import send_order_tool
from llm.tool.menu_tool import menu_recommend_tool
from llm.tool.confirm_order_checker import confirm_order_checker_tool
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
    # 构建上下文
    memory = memory_manager.get_memory(user_id, session_id)
    # 初始化智能体（zero-shot-agent）
    agent = initialize_agent(
        tools=[menu_recommend_tool, confirm_order_checker_tool, send_order_tool],
        llm=ds_model,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )
    # 构建提示词
    prompt = builder.build_prompt(input_text, user_id=user_id, location='location')
    # 下边注释测试用
    # prompt='''
    #     你是一个智能服务员，需要完成以下任务
    #     -理解用户需求
    #     -提供餐厅服务
    #     -处理客户投诉
    #     -推荐特色菜品
    #     当前用户请求:
    #         4人聚餐，来点香辣菜
    #         当前城市为 北京，
    #         推荐当地特色菜品如烤鸭, 炸酱面, 涮羊肉。
    #     用户画像分析:
    #         场景类型:聚餐
    #         参与人数:4
    #         -口味要求:香辣
    #     历史点单记录:
    #         无
    #     请根据以上信息综合判断并提供服务。
    # '''
    return agent.run(prompt)
