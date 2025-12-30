# 初始化数据库
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings

from langchain_community.vectorstores import FAISS

KB_DIR = Path("knowledge_db/docs")
VECTOR_DB_DIR = Path("knowledge_db/.vector_db")


def ingest_documents(modelName, dashscope_api_key):
    documents = []

    for file in KB_DIR.glob("*"):
        if file.suffix in [".md", ".txt"]:
            loader = TextLoader(str(file), encoding="utf-8")
            documents.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        separators=["### "],  # 优先级从前到后
        chunk_size=500,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(documents)

    embeddings = DashScopeEmbeddings(
        model= modelName,
        dashscope_api_key= dashscope_api_key
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTOR_DB_DIR)

    print(f"Ingested {len(chunks)} chunks into vector store.")

if __name__ == "__main__":
    EMBEDDING_MODEL_NAME="text-embedding-v4"
    EMBEDDING_MODEL_KEY="sk-d1964cfef7b1426fa6f54abb88377246"
    ingest_documents(EMBEDDING_MODEL_NAME, EMBEDDING_MODEL_KEY)
