"""
本模块用于初始化并构建本地知识库向量索引（RAG - Ingestion 阶段）。

模块职责：
- 从指定目录中加载本地文档（Markdown / Text）
- 对文档进行分块（Chunking）
- 使用向量模型生成 Embedding
- 构建并持久化向量数据库（FAISS）

设计说明：
- 当前采用 FAISS 作为本地向量存储，适合单机 / Demo / 面试场景
- 文档切分策略针对 Markdown 标题结构进行了简单优化
- Embedding 模型通过参数注入，便于后续替换
"""

# ===== 标准库 =====
from pathlib import Path
import os

# ===== 第三方库 =====
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS


# ===== 路径配置 =====
# 本地知识库原始文档目录
KB_DIR = Path("knowledge_db/docs")

# 向量数据库持久化目录
VECTOR_DB_DIR = Path("knowledge_db/.vector_db")


def ingest_documents(model_name: str, dashscope_api_key: str) -> None:
    """
    执行知识库文档的向量化与索引构建。

    该函数会完成以下流程：
    1. 加载本地 Markdown / Text 文档
    2. 按指定规则进行文本切分
    3. 使用 Embedding 模型生成向量
    4. 构建 FAISS 向量索引并保存到本地

    Args:
        model_name: Embedding 模型名称
        dashscope_api_key: DashScope API Key
    """

    documents = []

    # ===== 加载本地文档 =====
    for file_path in KB_DIR.glob("*"):
        if file_path.suffix in {".md", ".txt"}:
            loader = TextLoader(
                str(file_path),
                encoding="utf-8",
            )
            documents.extend(loader.load())

    if not documents:
        print("⚠️ 未在知识库目录中发现可用文档。")
        return

    # ===== 文本切分（Chunking） =====
    # 使用递归切分器，并优先按 Markdown 标题进行分割
    splitter = RecursiveCharacterTextSplitter(
        separators=["### "],  # 优先按三级标题切分
        chunk_size=500,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(documents)

    # ===== 初始化 Embedding 模型 =====
    embeddings = DashScopeEmbeddings(
        model=model_name,
        dashscope_api_key=dashscope_api_key,
    )

    # ===== 构建向量数据库 =====
    vectorstore = FAISS.from_documents(chunks, embeddings)

    # 持久化向量索引到本地
    vectorstore.save_local(VECTOR_DB_DIR)

    print(f"✅ 成功向量化并索引 {len(chunks)} 个文本块。")


if __name__ == "__main__":
    """
    脚本入口：
    用于在本地一次性完成知识库的初始化构建。
    """

    # 加载 .env 中的环境变量
    load_dotenv()

    # 从环境变量中读取 Embedding 配置（避免明文写入代码）
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-v4")
    EMBEDDING_MODEL_KEY = os.getenv("DASHSCOPE_API_KEY", "")

    if not EMBEDDING_MODEL_KEY:
        raise RuntimeError("❌ 未检测到 DASHSCOPE_API_KEY，请先配置环境变量。")

    ingest_documents(
        model_name=EMBEDDING_MODEL_NAME,
        dashscope_api_key=EMBEDDING_MODEL_KEY,
    )
