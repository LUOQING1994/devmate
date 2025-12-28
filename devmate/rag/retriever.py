import os
from pathlib import Path
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS

VECTOR_DB_DIR = Path("devmate/.vector_db")


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

    def retrieve(self, query: str, k: int = 4) -> list[dict]:
        docs = self.vectorstore.similarity_search(query, k=k)

        results = []
        for i, doc in enumerate(docs):
            results.append({
                "source": doc.metadata.get("source", "unknown"),
                "chunk_id": i,
                "content": doc.page_content
            })

        return results
