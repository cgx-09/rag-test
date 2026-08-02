## 项目一：命令行知识问答助手（第 1-2 周）

### 目标
做一个能从本地 PDF/TXT 文件中检索信息并回答问题的命令行工具。

### 做完你会什么
- 大模型 API 调用
- Prompt 工程基础
- 文本切分 + Embedding + 向量存储
- 基础 RAG 流程

### 知识点（边做边查）
| 做的时候遇到 | 去学什么 |
|-------------|---------|
| 怎么调大模型 API | OpenAI / DeepSeek API 文档，同步调用 vs 流式输出 |
| 怎么把文档变成向量 | Embedding 原理，推荐用 `text-embedding-3-small` 或 BGE |
| 文档太长怎么办 | 文本切分策略：chunk_size、chunk_overlap 怎么选 |
| 向量存哪里 | Chroma 本地存储，上手最简单 |
| 怎么把检索结果拼给模型 | Prompt 模板设计，上下文窗口控制 |

### 验收标准
- ✅ 能读取 PDF/TXT 文件
- ✅ 输入问题，返回基于文档内容的回答
- ✅ 回答能标注信息来源（哪个文档、哪一段）

---

## 项目二：带工具的对话 Agent（第 3-5 周）

### 目标
做一个能调用外部工具的 Agent，比如：查天气、算汇率、查数据库，用户用自然语言下指令，Agent 自己判断该调哪个工具。

### 做完你会什么
- Function Calling / Tool Calling 机制
- Agent 决策循环（ReAct）
- LangChain Agent 框架
- 工具定义与异常处理

### 知识点（边做边查）
| 做的时候遇到 | 去学什么 |
|-------------|---------|
| 怎么让模型自己决定调哪个工具 | Function Calling 机制，工具用 JSON Schema 描述 |
| Agent 怎么"思考-行动-观察" | ReAct 框架原理 |
| 怎么串联多个工具 | LangChain Agent + Tool 注册机制 |
| 工具调用报错了怎么办 | 异常兜底、重试、超时处理 |
| 怎么记住用户之前说了什么 | 对话记忆（ConversationBufferMemory / Summary） |

### 推荐工具集
- 天气查询（接一个免费 API）
- 汇率换算
- SQLite 数据库查询
- 计算器（复杂数学运算）

### 验收标准
- ✅ 用户说"北京明天天气怎么样"，Agent 自动调用天气工具
- ✅ 用户说"帮我查一下上个月销售额"，Agent 生成 SQL 并查询
- ✅ 工具调用失败时能友好提示而非崩溃

---

## 项目三：企业知识库 Agent（Web 版）（第 6-9 周）

### 目标
把项目一升级成带 Web 界面的完整知识库系统，支持文档上传、多轮对话、来源追溯。这个项目是简历核心亮点。

### 做完你会什么
- 完整 RAG 链路优化（重排序、混合检索）
- Web 前后端开发
- 流式输出
- Docker 部署

### 知识点（边做边查）
| 做的时候遇到 | 去学什么 |
|-------------|---------|
| 检索不准怎么办 | 混合检索（向量+BM25关键词）、重排序（Reranker） |
| 怎么切分更好 | 语义切分 vs 固定长度，按段落/标题切分 |
| 知识库文档更新了怎么办 | 增量更新策略，用 hash 检测变更 |
| 怎么搭前端 | Streamlit（最快）或 Gradio |
| 怎么做流式回答 | SSE (Server-Sent Events) + FastAPI |
| 怎么部署上线 | Docker + Docker Compose |

### 技术栈
- 后端：FastAPI + LangChain
- 前端：vue+vite
- 向量库：Chroma（开发）→ Milvus（生产演示）
- 部署：Docker

### 验收标准
- ✅ 网页端上传文档 → 自动解析向量化
- ✅ 多轮对话，支持追问
- ✅ 回答标注引用来源
- ✅ 有一个在线可访问的 Demo 链接

---

## 项目四：多 Agent 协作系统（第 10-12 周）

### 目标
做一个多 Agent 协作的复杂任务系统，比如"调研报告生成器"：一个 Agent 负责搜集信息，一个负责分析整理，一个负责写报告，一个负责审核质量。

### 做完你会什么
- 多 Agent 架构设计
- LangGraph 状态编排
- Agent 间通信与任务分发
- MCP 协议（加分）

### 知识点（边做边查）
| 做的时候遇到 | 去学什么 |
|-------------|---------|
| 多个 Agent 怎么分工协作 | Multi-Agent 架构模式：串行/并行/层级 |
| 怎么管理执行状态 | LangGraph 状态图、节点、条件路由 |
| Agent 之间怎么传数据 | 共享状态、消息传递 |
| 某个 Agent 出错了怎么办 | 失败重试、降级策略、人工介入节点 |
| 怎么接入更多外部工具 | MCP 协议基础 |

### 推荐选题（选一个）
1. **调研报告 Agent**：搜索 → 整理 → 写报告 → 审核
2. **代码助手 Agent**：需求分析 → 写代码 → 测试 → Review
3. **客服分流 Agent**：意图识别 → 路由到不同专业 Agent

### 验收标准
- ✅ 至少 3 个 Agent 协作完成一个完整任务
- ✅ 有状态追踪，能看到每个 Agent 的执行过程
- ✅ 有错误处理和重试机制

---

## 学习资源速查

| 需要什么 | 去哪里找 |
|---------|---------|
| LangChain 入门 | [官方教程](https://python.langchain.com/docs/get_started/) |
| LangGraph 入门 | [官方文档](https://langchain-ai.github.io/langgraph/) |
| RAG 实战 | [DeepLearning.AI 短课](https://www.deeplearning.ai/short-courses/)（免费） |
| Prompt 工程 | [OpenAI 最佳实践](https://platform.openai.com/docs/guides/prompt-engineering) |
| FastAPI 入门 | [官方教程](https://fastapi.tiangolo.com/tutorial/) |
| Streamlit 入门 | [官方文档](https://docs.streamlit.io/) |
| Agent 面试题 | 牛客网搜索"Agent 面经" |

---

## 每周时间分配建议

```
周一-周三  做项目（写代码、调 bug）    约 10h
周四-周五  补知识（看文档、看教程）     约 6h
周末       整理笔记 + 写 README        约 4h
```

## 里程碑检查

| 时间点 | 你应该能做到 |
|--------|-------------|
| 第 2 周末 | 命令行 RAG 问答跑通 |
| 第 5 周末 | 能调工具的 Agent 跑通 |
| 第 9 周末 | 有 Web 界面的知识库上线 |
| 第 12 周末 | 多 Agent 系统完成，开始投简历 |