
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from mcp_server.client import MCPSearchClient
from devmate.rag.retriever import LocalRAGRetriever

class ProgramAgent():

    def __init__(self, config):
        self.config = config
        #  == 提示词 =================
        self.program_prompts = config.prompts[0]
        self.summary_prompts = config.prompts[1]
        self.knowledge_prompts = config.prompts[2]
        self.unify_context_prompts = config.prompts[3]
        #  ==========================
        
        #  == 模型基础配置 =================
        llm_model = config.model_names[0]
        embeed_model = config.model_names[1]
        #  ==========================
        
        #  == 秘钥基础配置 =================
        llm_model_key = config.api_keys[0]
        embeed_model_key = config.api_keys[1]
        
        # 初始化后端大模型
        self.client = ChatOpenAI(
            model = llm_model,
            api_key = llm_model_key,
            base_url = config.api_base_url,
            temperature = 0.8,
            streaming = True
        )

        # 初始化MCP客户端
        self.mcp_client = MCPSearchClient()
        
        # 初始化向量数据库
        self.rag_retriever = LocalRAGRetriever(embeed_model, embeed_model_key)


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

    async def unify_context(
        self,
        user_input: str,
        rag_chunks: list[dict],
        web_summary: str | None,
    ) -> str:
        rag_text = "\n".join(
            f"- ({c['source']}#chunk{c['chunk_id']}): {c['content']}"
            for c in rag_chunks
        )

        messages = [
            SystemMessage(
                content=self.unify_context_prompts.format(
                    question=user_input,
                    rag_context=rag_text,
                    web_context=web_summary or "None",
                )
            )
        ]

        chunks = []
        async for chunk in self.client.astream(messages):
            if chunk.content:
                chunks.append(chunk.content)

        return "".join(chunks)

    async def stream(self, user_input: str, user_id: str, conversation_id: str = ""):
        messages = [
            SystemMessage(content=self.program_prompts),
            HumanMessage(content=user_input),
        ]

        # ====== 1️⃣ RAG 本地检索 ======
        yield "[RAG] Retrieving local knowledge...\n"
        rag_chunks = self.rag_retriever.retrieve(user_input)

        # ====== 2️⃣ MCP Web Search（可选） ======
        web_summary = None
        if self.need_search(user_input):
            yield "[Tool] Searching web...\n"
            raw_search = await self.mcp_client.search(user_input)
            web_summary = await self.summarize_search_results(raw_search)

        # ====== 3️⃣ 统一上下文摘要（🔥 G） ======
        yield "[Thinking] Consolidating knowledge from multiple sources...\n"
        unified_context = await self.unify_context(
            user_input,
            rag_chunks,
            web_summary
        )

        # ====== 4️⃣ 注入上下文（🔥 H） ======
        # 保证有数据输入
        if len(unified_context):
            messages.append(
                SystemMessage(
                    content=(self.knowledge_prompts.format(unified_context = unified_context))
                )
            )

        # ====== 5️⃣ 最终回答（Streaming） ======
        for chunk in self.client.stream(messages):
            if chunk.content:
                print(chunk.content)
                yield chunk.content
