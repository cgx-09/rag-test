"""Pydantic 模型，字段名与前端契约（camelCase）逐字对应。

前端 types/index.ts 约定：
- DocumentInfo: {id, name, size, status, chunksCount, uploadedAt}
- KnowledgeStats: {totalDocs, totalChunks}
- UploadResult: {id, name, status, message?}
- ChatRequest: {question, thread_id}
"""
from enum import Enum

from pydantic import BaseModel


class DocStatus(str, Enum):
    indexing = "indexing"
    ready = "ready"
    error = "error"


class DocumentInfo(BaseModel):
    id: str
    name: str
    size: int
    status: DocStatus
    chunksCount: int
    uploadedAt: str


class KnowledgeStats(BaseModel):
    totalDocs: int
    totalChunks: int


class UploadResult(BaseModel):
    id: str
    name: str
    status: DocStatus
    message: str | None = None


class ChatRequest(BaseModel):
    question: str
    thread_id: str


class Citation(BaseModel):
    documentName: str
    chunkIndex: int
    content: str
