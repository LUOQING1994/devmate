from langchain_core.tools import tool
from knowledge_db.rag.retriever import LocalRAGRetriever

# 1. 初始化你的检索类
EMBEDDING_MODEL_NAME = "text-embedding-v4"
EMBEDDING_MODEL_KEY = "sk-d1964cfef7b1426fa6f54abb88377246"
rag_engine = LocalRAGRetriever(EMBEDDING_MODEL_NAME, EMBEDDING_MODEL_KEY)

# 2. 定义 Tool
@tool
def query_knowledge_base(query: str) -> str:
    """
    当用户询问关于 DevMate 的功能、定义、技术细节或本地私有知识库中的信息时，使用此工具。
    输入应该是具体的查询问题。
    """
    # 调用你现有的方法
    
    
    results = rag_engine.search_knowledge_recall(query, k=3)
    
    return results