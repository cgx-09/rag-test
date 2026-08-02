"""6 个 API 端点 + 健康检查，前缀 /api。

前端契约要点：
- 所有非流式 2xx 响应必须返回合法 JSON（前端 wrapper 一律 res.json()）
- 响应字段 camelCase；聊天请求体 snake_case thread_id
"""
import os
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

import backend.config as config
from backend import rag_service, registry
from backend.chat import chat_stream
from backend.schemas import ChatRequest, DocumentInfo, KnowledgeStats, UploadResult

router = APIRouter()

SUPPORTED_EXT = ("pdf", "txt", "md")


def _allowed_ext(filename: str) -> bool:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in SUPPORTED_EXT


# ---------- 聊天 ----------
@router.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        chat_stream(request),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------- 文档管理 ----------
@router.get("/docs", response_model=list[DocumentInfo])
def list_docs():
    return [DocumentInfo(**d) for d in registry.list_documents()]


@router.get("/kb/stats", response_model=KnowledgeStats)
def kb_stats():
    docs = registry.list_documents()
    return KnowledgeStats(
        totalDocs=len(docs),
        totalChunks=sum(d["chunksCount"] for d in docs),
    )


@router.delete("/docs/{doc_id}")
def delete_doc(doc_id: str):
    doc = registry.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    rag_service.delete_by_source(doc["source"])
    registry.delete_document(doc_id)
    # 尽力删除上传文件
    try:
        file_path = os.path.join(config.UPLOAD_DIR, doc["source"])
        if os.path.isfile(file_path):
            os.remove(file_path)
    except OSError:
        pass
    return {}


@router.post("/docs/{doc_id}/reindex")
def reindex_doc(doc_id: str):
    doc = registry.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    file_path = os.path.join(config.UPLOAD_DIR, doc["source"])
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="原始文件不存在，无法重新索引")
    try:
        rag_service.delete_by_source(doc["source"])
        chunk_count = rag_service.index_file(file_path, doc["name"], doc["size"])
        registry.update_document(doc_id, chunksCount=chunk_count, status="ready")
    except Exception as e:  # noqa: BLE001
        registry.update_document(doc_id, status="error")
        raise HTTPException(status_code=500, detail=str(e))
    return {}


# ---------- 上传 ----------
@router.post("/upload", response_model=UploadResult)
async def upload(file: UploadFile = File(...)):
    original_name = file.filename or "unnamed"
    if not _allowed_ext(original_name):
        raise HTTPException(status_code=400, detail="仅支持 PDF / TXT / MD 文件")

    # 纯 ASCII 安全文件名：uuid 前缀 + 清理后的原名（避免中文路径 mojibake）
    stem, ext = os.path.splitext(original_name)
    safe_stem = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in stem)
    safe_name = f"{uuid.uuid4().hex}_{safe_stem}{ext.lower()}"
    saved_path = os.path.join(config.UPLOAD_DIR, safe_name)
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

    size = 0
    try:
        with open(saved_path, "wb") as f:
            while chunk := await file.read(1024 * 1024):
                f.write(chunk)
                size += len(chunk)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"保存文件失败: {e}")

    source = safe_name  # Chroma 的 source 键 = 上传文件 basename
    try:
        chunk_count = rag_service.index_file(saved_path, original_name, size)
        doc = registry.add_document(
            name=original_name,
            source=source,
            size=size,
            chunks_count=chunk_count,
            status="ready",
        )
        return UploadResult(id=doc["id"], name=original_name, status="ready")
    except Exception as e:  # noqa: BLE001
        doc = registry.add_document(
            name=original_name,
            source=source,
            size=size,
            chunks_count=0,
            status="error",
        )
        return UploadResult(id=doc["id"], name=original_name, status="error", message=str(e))


# ---------- 健康检查 ----------
@router.get("/health")
def health():
    return {"status": "ok"}
