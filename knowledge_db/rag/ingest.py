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
from langchain_text_splitters import MarkdownHeaderTextSplitter
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

    all_chunks = [] # 用于存放最终切分好的 chunk

    # ===== 加载本地文档 =====
    for file_path in KB_DIR.glob("*"):
        if file_path.suffix in {".md", ".txt"}:
            loader = TextLoader(str(file_path), encoding="utf-8")
            # 注意：load() 返回的是 List[Document]
            docs_from_file = loader.load()

            # ===== 文本切分（针对每个文件） =====
            headers_to_split_on = [("###", "Header 3")]
            markdown_splitter = MarkdownHeaderTextSplitter(
                headers_to_split_on=headers_to_split_on, 
                strip_headers=False
            )

            for doc in docs_from_file:
                # 1. 提取原始元数据（包含 source）
                original_metadata = doc.metadata 

                # 2. 执行 Markdown 逻辑切分
                # 注意：这里返回的是 List[Document]，metadata 里只有 Header 信息
                md_header_splits = markdown_splitter.split_text(doc.page_content)

                # 3. 手动将原始元数据（source）补回给每一个 md_split 对象
                for md_split in md_header_splits:
                    # 合并字典：保留 Header 标题，同时加入原始的 source 信息
                    md_split.metadata.update(original_metadata)

                # 4. 执行二次切分（处理超长块）
                # split_documents 会自动保留已有的 metadata
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
                chunks = text_splitter.split_documents(md_header_splits)
                
                all_chunks.extend(chunks)

    if not all_chunks:
        print("⚠️ 未发现可用文档或切分失败。")
        return

    # ===== 初始化 Embedding 模型 =====
    embeddings = DashScopeEmbeddings(
        model=model_name,
        dashscope_api_key=dashscope_api_key,
    )

    # ===== 构建向量数据库 =====
    vectorstore = FAISS.from_documents(all_chunks, embeddings)

    # 持久化向量索引到本地
    vectorstore.save_local(VECTOR_DB_DIR)

    print(f"✅ 成功向量化并索引 {len(all_chunks)} 个文本块。")


if __name__ == "__main__":
    """
    脚本入口：
    用于在本地一次性完成知识库的初始化构建。
    """
    
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

    ingest_documents(
        model_name=EMBEDDING_MODEL_NAME,
        dashscope_api_key=EMBEDDING_MODEL_KEY,
    )
