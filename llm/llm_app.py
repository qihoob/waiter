import getpass
import os
from collector.prompt_builder.prompt import PromptBuilder
from langchain_deepseek import ChatDeepSeek
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from memory.redis_memory_manager import RedisMemoryManager

if not os.getenv("DEEPSEEK_API_KEY"):
    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("Enter your DeepSeek API key: ")

# 构建提示词模板生成器
builder = PromptBuilder(max_length=512)
# 构建内存管理对象，以获取用户历史对话记录
memory_manager = RedisMemoryManager()

ds_model = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)


def build_chain(user_id: str, session_id: str, input_text):
    memory = memory_manager.get_memory(user_id, session_id)
    # 构建提示词
    prompt = builder.build_prompt(input_text, user_id=user_id, location='location')
    # 返回两个对象
    return ConversationChain(prompt=PromptTemplate.from_template(prompt), llm=ds_model, memory=memory)
