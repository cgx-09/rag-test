"""RAG 服务：封装 rag/rag.py，向路由层提供检索/索引/删除/统计能力。

不缓存 Chroma 客户端：每次操作打开全新连接，避免多客户端并发写同一目录
导致的 SQLite 锁冲突与读到陈旧数据的问题（本应用为低并发开发场景，开销可接受）。
"""
import os

import rag.rag as rag_mod

import backend.config as config
from backend.schemas import Citation


def get_vectorstore():
    """打开（必要时创建）现役向量库。"""
    return rag_mod.load_vectorstore(config.DB_DIR)


def retrieve(question: str):
    """检索 top-k 块，返回 (docs, sources)。sources 为前端 Citation 列表。"""
    vs = get_vectorstore()
    retriever = vs.as_retriever(search_kwargs={"k": config.TOP_K})
    docs = retriever.invoke(question)
    sources = [_to_citation(doc) for doc in docs]
    return docs, sources


def _to_citation(doc) -> Citation:
    meta = doc.metadata or {}
    source = meta.get("source", "")
    name = meta.get("doc_name") or os.path.basename(source) or "未知文档"
    idx = meta.get("chunk_index", 0)
    content = doc.page_content or ""
    if len(content) > config.CITATION_MAX_LEN:
        content = content[: config.CITATION_MAX_LEN] + "…"
    return Citation(documentName=name, chunkIndex=int(idx), content=content)


def delete_by_source(source: str) -> None:
    vs = get_vectorstore()
    vs.delete(where={"source": source})


def index_file(saved_path: str, doc_name: str, size: int) -> int:
    """加载→切分→写入 chunk 元数据→向量化存储。返回块数。"""
    docs = rag_mod.load_document(saved_path)
    chunks = rag_mod.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["source"] = os.path.basename(saved_path)
        chunk.metadata["doc_name"] = doc_name
        chunk.metadata["chunk_index"] = i
    rag_mod.build_vectorstore(chunks, persist_directory=config.DB_DIR)
    return len(chunks)


def list_chroma_docs() -> list[dict]:
    """按 source 分组的全部 chunk 统计，供启动对账用。"""
    vs = get_vectorstore()
    got = vs._collection.get(include=["metadatas"])
    groups: dict[str, dict] = {}
    for meta in got.get("metadatas") or []:
        src = (meta or {}).get("source", "")
        if src not in groups:
            groups[src] = {"source": src, "count": 0}
        groups[src]["count"] += 1
    return list(groups.values())
