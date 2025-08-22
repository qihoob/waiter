from typing import Optional, Dict, Any
from langchain.agents import initialize_agent
from langchain.agents.agent_types import AgentType
from llm.tool.call_kitchen_api import send_order_tool
from llm.tool.menu_tool import menu_recommend_tool
from llm.tool.confirm_order_checker import confirm_order_checker_tool
from langchain_deepseek import ChatDeepSeek
from memory.redis_memory_manager import RedisMemoryManager
from prompt_builder.prompt import PromptBuilder

# === 可选：餐厅数据/菜单等的仓储层（示例占位）===
class RestaurantRepo:
    """按需替换为真实数据库查询"""
    def get_restaurant_profile(self, restaurant_id: str) -> Dict[str, Any]:
        # 示例返回：位置、营业状态、推荐配置等
        return {
            "restaurant_id": restaurant_id,
            "name": "演示餐厅",
            "location": "北京",            # 可用于 PromptBuilder 的 location
            "opening_hours": "10:00-22:00"
        }

    def get_menu_snapshot(self, restaurant_id: str) -> Dict[str, Any]:
        # 也可以不在这里返回；menu_recommend_tool 自己查
        return {
            "sections": [
                {"name": "特色", "items": ["宫保鸡丁", "酸辣土豆丝", "烤鸭"]},
            ]
        }

class AgentService:
    def __init__(self):
        self.memory_manager = RedisMemoryManager()
        self.prompt_builder = PromptBuilder()
        self.repo = RestaurantRepo()

        # 你的模型定义（保持与你粘贴的代码一致）
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        self.tools = [menu_recommend_tool, confirm_order_checker_tool, send_order_tool]

    def run(
        self,
        user_id: str,
        session_id: str,
        input_text: str,
        restaurant_id: str,
        table_id: Optional[str] = None,
    ) -> str:
        """
        把 /api/chat 收到的参数 + /start 消息里建立的上下文，一起交给 LangChain 智能体
        """
        # 1) 取对话记忆
        memory = self.memory_manager.get_memory(user_id, session_id)

        # 2) 拉取餐厅/菜单等上下文（可选）
        profile = self.repo.get_restaurant_profile(restaurant_id)
        location = profile.get("location") or "未知地区"

        # 3) 初始化 Agent（Zero-shot ReAct + 工具）
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=memory,
            verbose=True
        )

        # 4) 构建提示词
        # prompt = self.prompt_builder.build_prompt(
        #     input_text,
        #     user_id=user_id,
        #     location=location,
        # )
        prompt='''
            你是一个智能服务员，需要完成以下任务
            -理解用户需求
            -提供餐厅服务
            -处理客户投诉
            -推荐特色菜品
            当前用户请求:
                4人聚餐，来点香辣菜
                当前城市为 北京，
                推荐当地特色菜品如烤鸭, 炸酱面, 涮羊肉。
            用户画像分析:
                场景类型:聚餐
                参与人数:4
                -口味要求:香辣
            历史点单记录:
                无
            请根据以上信息综合判断并提供服务。
        '''

        # 5) 把更多上下文给到模型（例如桌位/就餐人数），可以在 prompt 里拼接：
        extra_ctx = f"\n[系统上下文] 餐厅ID={restaurant_id} 桌位ID={table_id or '未知'} 会话ID={session_id}\n"
        final_prompt = prompt + extra_ctx



        # 6) 运行
        reply = agent.run(final_prompt)
        return reply