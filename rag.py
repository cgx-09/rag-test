"""
RAG 核心模块
负责：文档加载 → 文本切分 → 向量化存储 → 检索 → 生成回答
"""
import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 加载环境变量
load_dotenv()

# ============ 配置区 ============
CHUNK_SIZE = 500        # 每个文本块的大小（字符数）
CHUNK_OVERLAP = 50      # 相邻块之间的重叠（防止上下文断裂）
TOP_K = 3               # 检索时返回最相关的 K 个文档块
# =================================


def get_llm() -> ChatOpenAI:
    """初始化大模型"""
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME", "deepseek-chat"),
        api_key=os.getenv("API_KEY"),  # DeepSeek 或 OpenAI 的 API Key
        base_url=os.getenv("BASE_URL", "https://api.deepseek.com"),
        temperature=0.3,  # 低一点让回答更稳定
    )


def get_embeddings():
    """使用本地 Ollama 的 BGE-M3 模型生成向量"""
    return OllamaEmbeddings(
        model="modelscope.cn/gpustack/bge-m3-GGUF:latest",
        base_url="http://localhost:11434",  # Ollama 默认服务地址
    )


def load_document(file_path: str):
    """
    加载文档，支持 PDF 和 TXT
    返回：Document 对象列表
    """
    ext = file_path.lower().split(".")[-1]
    if ext == "pdf":
        loader = PyPDFLoader(file_path)
    elif ext in ("txt", "md"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"暂不支持 .{ext} 格式，请使用 PDF 或 TXT 文件")
    
    docs = loader.load()
    print(f"✅ 已加载文件：{file_path}，共 {len(docs)} 页/段")
    return docs


def split_documents(docs):
    """
    将文档切分成小块
    为什么要切分？因为大模型有上下文长度限制，而且小块检索更精准
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", ".", " ", ""],  # 优先按段落切分
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ 已切分为 {len(chunks)} 个文本块")
    return chunks


def build_vectorstore(chunks, persist_directory="./chroma_db"):
    """
    将文本块向量化并存入 Chroma 向量数据库
    persist_directory：本地存储路径，下次启动可以直接加载
    """
    embeddings = get_embeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )
    print(f"✅ 已向量化存储到 {persist_directory}")
    return vectorstore


def load_vectorstore(persist_directory="./chroma_db"):
    """加载已有的向量数据库"""
    embeddings = get_embeddings()
    return Chroma(persist_directory=persist_directory, embedding_function=embeddings)


def format_docs(docs):
    """将检索到的文档格式化为字符串，拼入 Prompt"""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def build_qa_chain(vectorstore):
    """
    构建问答链
    流程：用户提问 → 检索相关文档 → 拼入 Prompt → 大模型生成回答
    """
    llm = get_llm()
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    # Prompt 模板：告诉模型只根据检索内容回答，不要编造
    prompt = ChatPromptTemplate.from_template("""
你是一个知识问答助手。请严格根据以下参考资料回答用户的问题。
如果参考资料中没有相关信息，请回答"根据已有资料无法回答这个问题"。
不要编造参考资料中没有的内容。

参考资料：
{context}

用户问题：{question}

请回答：
""")

    # 构建链：检索 → 格式化 → 拼 Prompt → 模型回答
    qa_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return qa_chain


def ask(qa_chain, question: str):
    """问一个问题，返回回答"""
    return qa_chain.invoke(question)


# ============ 快速测试 ============
if __name__ == "__main__":
    # 测试：加载一个示例文档
    print("🧪 测试 RAG 模块...")
    
    # 创建一个测试文件
    test_file = "test_sample.txt"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("""
LangChain 是一个用于构建大语言模型应用的框架。
它提供了链（Chain）、Agent、工具（Tool）等核心组件。
LangChain 支持 OpenAI、Anthropic、本地模型等多种大模型。
RAG（检索增强生成）是 LangChain 最常用的应用场景之一。
Chroma 是一个轻量级的向量数据库，适合本地开发和测试。
""")
    
    docs = load_document(test_file)
    chunks = split_documents(docs)
    vs = build_vectorstore(chunks, persist_directory="./test_chroma_db")
    chain = build_qa_chain(vs)
    
    result = ask(chain, "LangChain 是什么？")
    print(f"\n💬 回答：{result}")

if __name__ == "__main__":
    # ... (保留你原有的测试代码) ...

    # 添加以下代码来查看存储情况
    print("\n📊 向量存储状态：")
    # 加载已有的向量库（如果存在）
    if os.path.exists("./test_chroma_db"):
        loaded_vs = load_vectorstore("./test_chroma_db")
        # 获取所有文档的数量（注意：这个方法可能因版本而异）
        try:
            # 尝试获取集合的计数
            count = loaded_vs._collection.count()
            print(f"✅ 测试库中已存储的文本块数量：{count}")
        except:
            print("⚠️ 无法直接获取计数，但文件已存在。")