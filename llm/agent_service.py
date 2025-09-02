from langchain_deepseek import ChatDeepSeek
from memory.redis_memory_manager import RedisMemoryManager

class AgentService:
    def __init__(self):
        self.memory_manager = RedisMemoryManager()
        self.prompt_builder = PromptBuilder()
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )


        memory = self.memory_manager.get_memory(user_id, session_id)
        agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=memory,
        )
        reply = agent.run(final_prompt)
        return reply