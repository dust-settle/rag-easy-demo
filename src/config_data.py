import os

from ollama import embeddings

# 使用绝对路径（相对本文件），保证"入库"和"检索"永远指向同一个库。
# 原来的 "./chroma_db" 依赖"当前工作目录"：从仓库根目录启动 streamlit 会写进
# <根目录>/chroma_db，而在这里跑 vector_stores.py 又读 <data>/chroma_db，
# 于是出现"上传成功却检索不到"。
BASE_DIR = os.path.dirname(os.path.abspath(__file__))       # src 目录（代码所在）
PROJECT_DIR = os.path.dirname(BASE_DIR)                      # project 目录
DATA_DIR = os.path.join(PROJECT_DIR, "data")                 # 源数据：知识库 txt
RUNTIME_DIR = os.path.join(PROJECT_DIR, "runtime")           # 运行时数据：不进 git

md5_path = os.path.join(RUNTIME_DIR, "md5.txt")

collection_name = "rag"
persist_directory = os.path.join(RUNTIME_DIR, "chroma_db")

chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n", "\n", "。", "!", "！", " ", ""]

max_split_char_number = 1000            # 文本分割的阈值

# v1.1：粗召回条数。原名叫 similarity_threshold（阈值），但它其实是"返回几条"，
# 不是相似度门槛，面试时容易说错，所以改名为 retrieve_k。
retrieve_k = 10               # 先粗召回 10 条，再交给 Reranker 精排

# v1.1：Reranker 精排配置
rerank_model_name = "gte-rerank-v2"   # DashScope 重排模型（已实测账号可用）
rerank_top_n = 3              # 精排后只留最相关的 3 条喂给大模型

embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen3.8-max"

session_config = {
    "configurable": {
        "session_id": "user_001"
    }
}