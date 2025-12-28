
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from mcp_server.client import MCPSearchClient

class ProgramAgent():

    def __init__(self, config):
        self.config = config
        self.program_prompts = config.prompts[0]
        self.summary_prompts = config.prompts[1]
        
        # 初始化后端大模型
        self.client = ChatOpenAI(
            model = config.model_name,
            api_key = config.api_key,
            base_url = config.api_base_url,
            temperature = 0.8,
            streaming = True
        )

        # 初始化MCP客户端
        self.mcp_client = MCPSearchClient()
        
    def reset(self):
        """
        重置对话状态，将所有属性恢复到初始状态
        """
        pass
    
    async def stop_chat(self):
        pass
    
    async def test_search(self):
        result = await self.mcp_client.search("北京今天的天气")
        return result
    
    def need_search(self, user_input: str) -> bool:
        """
        简单规则判断是否需要外部搜索
        """
        keywords = ["天气", "今天", "最新", "附近", "现在", "路线", "推荐"]
        return any(k in user_input for k in keywords)

    async def summarize_search_results(self, search_results: str) -> str:
        """
        Use LLM to summarize raw search results into concise context.
        """
        messages = [
            SystemMessage(content=self.summary_prompts.format(
                search_results=search_results
            ))
        ]

        summary_chunks = []
        async for chunk in self.client.astream(messages):
            if chunk.content:
                summary_chunks.append(chunk.content)

        return "".join(summary_chunks)

    async def stream(self, user_input: str, user_id: str, conversation_id: str = ""):
        messages = [
            SystemMessage(content=self.program_prompts),
            HumanMessage(content=user_input),
        ]

        # ====== 1️⃣ Planning ======
        if self.need_search(user_input):
            yield "[Planning] External information required.\n"

            # ====== 2️⃣ MCP Tool Call ======
            raw_search_result = await self.mcp_client.search(user_input)
            yield "[Tool: search_web] Raw search data retrieved.\n"

            # ====== 3️⃣ Search Result Compression ======
            yield "[Thinking] Summarizing search results...\n"
            summary = await self.summarize_search_results(raw_search_result)

            # ====== 4️⃣ Inject summarized context ======
            messages.append(
                SystemMessage(
                    content=(
                        "The following is a summarized result of web search:\n"
                        f"{summary}"
                    )
                )
            )

        # ====== 5️⃣ Final LLM Streaming Answer ======
        for chunk in self.client.stream(messages):
            if chunk.content:
                yield chunk.content
