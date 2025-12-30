"""
LocalRAGRetriever：本地知识库检索组件（RAG - Retrieval 阶段）。

模块职责：
- 加载本地已构建的向量数据库（FAISS）
- 基于用户查询执行相似度检索
- 返回带有来源信息的知识片段，支持可追溯性

设计说明：
- 本模块仅负责“召回”，不负责回答生成
- Embedding 模型通过参数注入，避免与 Ingestion 阶段强耦合
- 返回结构中保留 source 与 chunk 索引，便于后续引用与调试
"""

# ===== 标准库 =====
from pathlib import Path
from typing import List, Dict

# ===== 第三方库 =====
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS


# ===== 向量数据库路径 =====
VECTOR_DB_DIR = Path("knowledge_db/.vector_db")


class LocalRAGRetriever:
    """
    本地 RAG 知识库检索器。

    用于在已构建的 FAISS 向量索引中，
    根据用户查询召回最相关的知识片段。
    """

    def __init__(self, model_name: str, api_key: str):
        """
        初始化检索器并加载向量数据库。

        Args:
            model_name: Embedding 模型名称
            api_key: DashScope API Key
        """

        # 初始化 Embedding 模型（需与 Ingestion 阶段保持一致）
        self.embeddings = DashScopeEmbeddings(
            model=model_name,
            dashscope_api_key=api_key,
        )

        # 加载本地 FAISS 向量索引
        self.vectorstore = FAISS.load_local(
            VECTOR_DB_DIR,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def search_knowledge_recall(self, query: str, k: int = 4) -> List[Dict]:
        """
        在本地知识库中执行相似度检索。

        Args:
            query: 用户输入的自然语言查询
            k: 返回的相似文本块数量

        Returns:
            一个包含多个知识片段的列表，每个片段包含：
            - 来源文件
            - chunk 索引
            - 具体内容
        """

        docs = self.vectorstore.similarity_search(query, k=k)

        results: List[Dict] = []
        for idx, doc in enumerate(docs):
            results.append(
                {
                    "来源": doc.metadata.get("source", "unknown"),
                    "chunk索引": idx,
                    "内容": doc.page_content,
                }
            )

        return results


if __name__ == "__main__":
    """
    本地调试入口：
    用于快速验证知识库检索是否生效。
    """

    # 示例配置（生产环境中应通过环境变量或配置文件注入）
    EMBEDDING_MODEL_NAME = "text-embedding-v4"
    EMBEDDING_MODEL_KEY = "YOUR_DASHSCOPE_API_KEY"

    retriever = LocalRAGRetriever(
        model_name=EMBEDDING_MODEL_NAME,
        api_key=EMBEDDING_MODEL_KEY,
    )

    query = "DevMate 能做什么？"
    recall_results = retriever.search_knowledge_recall(query)

    for item in recall_results:
        print(item)
