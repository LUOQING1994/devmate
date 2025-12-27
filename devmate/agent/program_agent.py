from dotenv import load_dotenv
load_dotenv() 

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class ProgramAgent():

    def __init__(self, config):
        self.config = config
        self.prompts = config.prompts
        
        # 初始化后端大模型
        self.client = ChatOpenAI(
            model = config.model_name,
            api_key = config.api_key,
            base_url = config.api_base_url,
            temperature = 0.8,
            streaming = True
        )

    def reset(self):
        """
        重置对话状态，将所有属性恢复到初始状态
        """
        pass
    
    async def stop_chat(self):
        pass
            
    async def stream(self, user_input: str, user_id: str, conversation_id: str = ""):
        messages = [
            SystemMessage(content = self.prompts),
            HumanMessage(content = user_input),
        ]

        for chunk in self.client.stream(messages):
            if chunk.content:
                yield chunk.content

    async def run_with_events(self, user_input: str):
        # Planning 阶段
        yield ("planning", "分析用户需求，制定整体方案...")

        messages = [
            SystemMessage(content = self.prompts),
            HumanMessage(content = user_input),
        ]

        # LLM Streaming
        for chunk in self.client.stream(messages):
            if chunk.content:
                yield ("client", chunk.content)

        yield ("end", "")
        
    def match_chunk(self, chunk: str) -> bool:
        """
            功能说明:
            1. 获取条件分支3的结果 判断对应的分支路线
            2.  根据不同的分支 构建不同的数据
        """
            
        return "测试"
