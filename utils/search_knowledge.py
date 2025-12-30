import os
from langchain_core.tools import tool
from knowledge_db.rag.retriever import LocalRAGRetriever

# 2. 定义 Tool
@tool
def search_knowledge_base(query: str) -> str:
    """
    当用户询问关于 DevMate 的功能、定义、技术细节或本地私有知识库中的信息时，使用此工具。
    输入应该是具体的查询问题。
    """
    # 从环境变量中读取 Embedding 配置（避免明文写入代码）
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "")
    EMBEDDING_MODEL_KEY = os.getenv("EMBEDDING_MODEL_KEY", "")

    rag_engine = LocalRAGRetriever(EMBEDDING_MODEL_NAME, EMBEDDING_MODEL_KEY)
    
    results = rag_engine.search_knowledge_recall(query, k=3)
    
    return results