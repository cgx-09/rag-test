# 📚 RAG 知识问答助手

> 项目一：边做边学 AI Agent 开发
> 技术栈：LangChain + DeepSeek + Chroma

## 这是什么

一个命令行工具，能读取你的 PDF/TXT 文档，然后用自然语言向它提问，它会基于文档内容给出回答。

这就是最基础的 **RAG（检索增强生成）** 系统，是所有 AI Agent 应用的核心能力。

## 快速开始

### 1. 安装依赖

```bash
cd rag-assistant
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

然后编辑 `.env` 文件，填入你的 API Key：
- **DeepSeek**（推荐）：去 https://platform.deepseek.com 注册，有免费额度
- **OpenAI**：如果你有 OpenAI 的 Key 也可以用

### 3. 加载文档

把你的 PDF 或 TXT 文件放在项目目录下，然后：

```bash
python main.py load 你的文档.pdf
```

### 4. 开始提问

```bash
# 单次提问
python main.py ask "这篇文档讲了什么？"

# 多轮对话模式
python main.py chat
```

## 项目结构

```
rag-assistant/
├── main.py          # 入口文件，命令行交互
├── rag.py           # RAG 核心逻辑（重点看这个）
├── requirements.txt # Python 依赖
├── .env.example     # API Key 配置模板
├── .env             # 你的 API Key（不要提交到 git）
└── chroma_db/       # 向量数据库（运行后自动生成）
```

## 学习重点

这个项目虽小，但覆盖了 RAG 的完整链路：

```
文档加载 → 文本切分 → Embedding向量化 → 向量存储 → 相似度检索 → 拼Prompt → 大模型回答
```

### 关键概念

| 概念 | 解释 | 在代码里的位置 |
|------|------|--------------|
| Document Loader | 把文件读进内存 | `rag.py` → `load_document()` |
| Text Splitter | 把长文档切成小块 | `rag.py` → `split_documents()` |
| Embedding | 把文字变成向量（数字数组） | `rag.py` → `get_embeddings()` |
| Vector Store | 存储和检索向量 | `rag.py` → `build_vectorstore()` |
| Retriever | 根据问题找最相关的文档块 | `rag.py` → `build_qa_chain()` 里的 retriever |
| Prompt Template | 控制模型怎么回答 | `rag.py` → `build_qa_chain()` 里的 prompt |

### 思考题（做完项目后试着回答）

1. 为什么要把文档切块而不是整篇塞给模型？
方便模型存储加上模型调用
2. `CHUNK_SIZE` 和 `CHUNK_OVERLAP` 分别影响什么？
CHUNK_SIZE管理切分的字符数、CHUNK_OVERLAP管理上下文的连贯
3. 如果检索结果不准确，可以从哪些环节优化？
CHUNK_SIZE优化切分的更仔细一点、CHUNK_OVERLAP的上下文不连贯可以提高字符保持连贯性
4. 这个系统的"记忆"是什么？有长期记忆吗？

## 下一步

这个项目跑通后，下一步（项目二）要给它加上"工具调用"能力，让它不只能查文档，还能查天气、算数学、查数据库。

---

*开始你的 Agent 开发之旅吧！* 🚀
