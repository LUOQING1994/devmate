
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from tools.load_prompt import load_prompt

class SimpleAgent():

    def __init__(self, tools):
        #  == 提示词 =================
        program_prompts = load_prompt("program_prompt.txt")
        #  ==========================
        
        #  == 对话模型秘钥基础配置 =================
        llm_model_key = os.getenv("API_KEY", "")
        llm_api_base_url = os.getenv("AI_BASE_URL", "")
        llm_model = os.getenv("MODEL_NAME", "")

        # 初始化后端大模型
        model = ChatOpenAI(
            model = llm_model,
            api_key = llm_model_key,
            base_url = llm_api_base_url,
            temperature = 0.8,
            streaming = True
        )
        
        # 创建记忆存储 (Memory/Persistence)
        # 在最新的 LangChain 中，通过 checkpointer 实现跨轮次记忆
        memory = InMemorySaver()
        
        # 5. 创建智能体 (Agent)
        # 这是最新文档推荐的简化写法
        self.agent = create_agent(
            model=model,
            tools=tools,
            system_prompt= program_prompts,
            checkpointer = memory
        )
        
        # 6. 运行智能体并测试记忆功能
        # 我们通过 thread_id 来区分不同的对话线程（即“记忆”的索引）
        self.config = {"configurable": {"thread_id": "user_123"}}
     
    async def stream(self, user_input: str):

        input_obj = {"messages": [{"role": "user", "content": user_input }]}
        # LLM Streaming
        # async for chunk in self.agent.astream(input_obj, self.config, stream_mode="values"):
        #     yield chunk["messages"][-1]
        
        async for chunk in self.agent.astream(input_obj, self.config, stream_mode="values"):
            chunk["messages"][-1].pretty_print()

            