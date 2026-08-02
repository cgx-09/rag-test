"""FastAPI 入口。

运行方式（在仓库根目录执行）：
    uvicorn backend.main:app --reload --port 8000
前端 Vite 已把 /api 代理到 http://localhost:8000。
"""
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import backend.config as config
from backend import rag_service, registry
from backend.routes import router

# Windows 下 piped stdout 默认 GBK 编码，rag/rag.py 里的 ✅ 等 emoji print 会抛
# UnicodeEncodeError。统一转 UTF-8（errors=replace 兜底），不影响正常输出。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)
    # 启动对账：把现有 Chroma 数据与文档注册表同步
    try:
        registry.reconcile(rag_service.list_chroma_docs())
    except Exception as e:  # noqa: BLE001
        print(f"[startup] 文档对账失败（可忽略）：{e}")
    yield


app = FastAPI(title="企业知识库助手后端", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router, prefix="/api")
