import os
from pathlib import Path
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool

VECTOR_DB_DIR = Path("knowledge_db/.vector_db")


class LocalRAGRetriever:
    def __init__(self, modelName, api_key):
        self.embeddings = DashScopeEmbeddings(
            model= modelName,
            dashscope_api_key= api_key 
        )
        self.vectorstore = FAISS.load_local(
            VECTOR_DB_DIR,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def search_knowledge_recall(self, query: str, k: int = 4) -> list[dict]:
        docs = self.vectorstore.similarity_search(query, k=k)

        results = []
        for i, doc in enumerate(docs):
            results.append({
                "来源": doc.metadata.get("source", "unknown"),
                "chunk索引": i,
                "内容": doc.page_content
            })

        return results

if __name__ == "__main__":
    EMBEDDING_MODEL_NAME="text-embedding-v4"
    EMBEDDING_MODEL_KEY="sk-d1964cfef7b1426fa6f54abb88377246"
    localRagRetriever = LocalRAGRetriever(EMBEDDING_MODEL_NAME, EMBEDDING_MODEL_KEY)
    query = "DevMate能做什么"
    recall_datas = localRagRetriever.search_knowledge_base(query)
    print(recall_datas)
