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

    def search_knowledge_recall(self, query: str, k: int = 4, score_threshold: int = 0.6) -> List[Dict]:
        """
        在本地知识库中执行相似度检索。

        Args:
            query: 用户输入的自然语言查询
            k: 返回的相似文本块数量
            score_threshold: 相似度阈值。

        Returns:
            一个包含多个知识片段的列表，每个片段包含：
            - 来源文件
            - chunk 索引
            - 具体内容
        """

        # 按分数进行选择返回
        docs = self.vectorstore.similarity_search_with_score(query, k=k)

        results: List[Dict] = []
        for idx, (doc, score) in enumerate(docs):
            # 过滤逻辑：只保留距离小于阈值的片段
            if score > score_threshold:
                continue
            
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
    import os
    from dotenv import load_dotenv 
    # 1. 获取当前脚本的绝对路径
    current_file_path = Path(__file__).resolve()

    # 2. 找到项目的根目录 (即向上退一级): 
    project_root = current_file_path.parent.parent.parent

    # 3. 拼接 .env 的绝对路径: 
    env_path = project_root / ".env"

    # 4. 加载环境变量
    load_dotenv(dotenv_path=env_path)
    # 打印一下，方便在 Docker 日志里调试（可选）
    print(f"DEBUG: 正在尝试加载 .env 文件，路径: {env_path}")
    print(f"DEBUG: .env 文件是否存在: {env_path.exists()}")
    # 加载 .env 中的环境变量

    # 从环境变量中读取 Embedding 配置（避免明文写入代码）
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "")
    EMBEDDING_MODEL_KEY = os.getenv("EMBEDDING_MODEL_KEY", "")

    if not EMBEDDING_MODEL_KEY:
        raise RuntimeError("❌ 未检测到 EMBEDDING_MODEL_KEY，请先配置环境变量。")
    

    retriever = LocalRAGRetriever(
        model_name=EMBEDDING_MODEL_NAME,
        api_key=EMBEDDING_MODEL_KEY,
    )

    query = "DevMate 能做什么？"
    recall_results = retriever.search_knowledge_recall(query)

    for item in recall_results:
        print(item)
