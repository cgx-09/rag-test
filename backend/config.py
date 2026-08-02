"""后端全局配置：路径与常量。"""
import os

# 仓库根目录（backend/ 的上一级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 向量库沿用 rag/ 的现役库
DB_DIR = os.path.join(BASE_DIR, "rag", "chroma_db")

# 上传文件目录与文档注册表（均已被 .gitignore 忽略）
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")
REGISTRY_PATH = os.path.join(BASE_DIR, "data", "docs_registry.json")

# 检索返回的块数（与 rag/rag.py 一致）
TOP_K = 3

# 多轮对话历史上限（条数，含 user/assistant）
MAX_HISTORY = 10

# 前端引用内容截断长度
CITATION_MAX_LEN = 300
