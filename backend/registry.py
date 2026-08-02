"""文档元数据注册表：JSON 文件持久化，启动时与 Chroma 对账。

Chroma 只存 chunk 的 source 字符串，缺少前端需要的 doc 级元数据
（名称/大小/状态/上传时间），故用注册表作为 /api/docs、/kb/stats 的数据源。
"""
import json
import os
import uuid
from datetime import datetime

import backend.config as config


def load_registry() -> dict:
    """读取注册表，损坏或缺失时返回空结构。"""
    if os.path.exists(config.REGISTRY_PATH):
        try:
            with open(config.REGISTRY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and isinstance(data.get("documents"), list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"documents": []}


def save_registry(reg: dict) -> None:
    os.makedirs(os.path.dirname(config.REGISTRY_PATH), exist_ok=True)
    with open(config.REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def add_document(name: str, source: str, size: int, chunks_count: int, status: str = "ready") -> dict:
    reg = load_registry()
    doc = {
        "id": uuid.uuid4().hex,
        "name": name,
        "source": source,
        "size": size,
        "status": status,
        "chunksCount": chunks_count,
        "uploadedAt": _now_str(),
    }
    reg["documents"].insert(0, doc)
    save_registry(reg)
    return doc


def get_document(doc_id: str) -> dict | None:
    return next((d for d in load_registry()["documents"] if d["id"] == doc_id), None)


def list_documents() -> list[dict]:
    return load_registry()["documents"]


def delete_document(doc_id: str) -> None:
    reg = load_registry()
    reg["documents"] = [d for d in reg["documents"] if d["id"] != doc_id]
    save_registry(reg)


def update_document(doc_id: str, **fields) -> None:
    reg = load_registry()
    for d in reg["documents"]:
        if d["id"] == doc_id:
            d.update(fields)
            break
    save_registry(reg)


def reconcile(chroma_docs: list[dict]) -> None:
    """启动对账：
    1. 删除注册表中 Chroma 已不存在的条目；
    2. 为 Chroma 中存在但注册表缺失的（历史遗留）source 合成条目。
    """
    reg = load_registry()
    chroma_by_source = {cd["source"]: cd for cd in chroma_docs}

    kept = [d for d in reg["documents"] if d["source"] in chroma_by_source]
    known_sources = {d["source"] for d in kept}
    for src, cd in chroma_by_source.items():
        if src in known_sources:
            continue
        file_path = os.path.join(config.UPLOAD_DIR, src)
        size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
        kept.append(
            {
                "id": uuid.uuid4().hex,
                "name": os.path.basename(src) or src,
                "source": src,
                "size": size,
                "status": "ready",
                "chunksCount": cd["count"],
                "uploadedAt": _now_str(),
            }
        )
    kept.sort(key=lambda d: d["uploadedAt"], reverse=True)
    if kept != reg["documents"]:
        reg["documents"] = kept
        save_registry(reg)
