"""SSE 聊天：RAG 检索 → 流式生成 → done(sources)。

SSE 行格式与前端 api/index.ts 解析逻辑匹配：
    data: {"type":"token","content":"…"}
    data: {"type":"done","sources":[{documentName,chunkIndex,content}]}
    data: {"type":"error","error":"…"}
done / error 为最后一帧，其后生成器结束、流关闭。
"""
import json

import rag.rag as rag_mod

import backend.config as config
from backend import rag_service
from backend.schemas import ChatRequest

# 内存多轮历史：{thread_id: [messages]}，重启即失（与 InMemorySaver 同性质）
_history: dict[str, list[dict]] = {}

SYSTEM_TEMPLATE = """你是一个知识问答助手。请严格根据以下参考资料回答用户的问题。
如果参考资料中没有相关信息，请回答"根据已有资料无法回答这个问题"。
不要编造参考资料中没有的内容。

参考资料：
{context}"""


def _event_bytes(event: dict) -> bytes:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n".encode("utf-8")


def _text_of(chunk) -> str:
    content = getattr(chunk, "content", "") or ""
    if isinstance(content, list):  # 兼容多模态/工具块：只取文本部分
        return "".join(part.get("text", "") for part in content if isinstance(part, dict))
    return str(content)


async def chat_stream(request: ChatRequest):
    """产出 SSE 事件字节的异步生成器。"""
    try:
        # 1. 检索相关块，构建 sources
        docs, sources = rag_service.retrieve(request.question)
        context = rag_mod.format_docs(docs)

        # 2. 组装消息：system + 近期历史 + 当前问题
        llm = rag_mod.get_llm()
        history = _history.setdefault(request.thread_id, [])
        messages = [
            {"role": "system", "content": SYSTEM_TEMPLATE.format(context=context)},
            *history[-config.MAX_HISTORY:],
            {"role": "user", "content": request.question},
        ]

        # 3. 流式生成 token
        answer_parts: list[str] = []
        async for chunk in llm.astream(messages):
            token = _text_of(chunk)
            if token:
                answer_parts.append(token)
                yield _event_bytes({"type": "token", "content": token})

        # 4. 写入多轮历史（截断，防止无限增长）
        history.append({"role": "user", "content": request.question})
        history.append({"role": "assistant", "content": "".join(answer_parts)})
        if len(history) > config.MAX_HISTORY:
            del history[: len(history) - config.MAX_HISTORY]

        # 5. 结束帧
        yield _event_bytes(
            {"type": "done", "sources": [s.model_dump() for s in sources]}
        )
    except Exception as e:  # noqa: BLE001
        try:
            yield _event_bytes({"type": "error", "error": str(e)})
        except Exception:  # noqa: BLE001
            pass
