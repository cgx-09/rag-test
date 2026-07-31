"""
命令行知识问答助手 - 入口文件
用法：
    python main.py load <文件路径>    加载文档并建立索引
    python main.py ask <问题>        提问
    python main.py chat              进入多轮对话模式
"""
import sys
import os

# 把当前目录加到路径里
sys.path.insert(0, os.path.dirname(__file__))

from rag import (
    load_document,
    split_documents,
    build_vectorstore,
    load_vectorstore,
    build_qa_chain,
    ask,
)

DB_DIR = "./chroma_db"


def cmd_load(file_path: str):
    """加载文档，建立向量索引"""
    print(f"\n📖 正在加载文档：{file_path}")
    print("-" * 40)
    
    docs = load_document(file_path)
    chunks = split_documents(docs)
    build_vectorstore(chunks, persist_directory=DB_DIR)
    
    print("-" * 40)
    print("✅ 索引建立完成！现在可以用 ask 或 chat 命令提问了。")


def cmd_ask(question: str):
    """单次提问"""
    if not os.path.exists(DB_DIR):
        print("❌ 还没有建立索引，请先用 load 命令加载文档")
        return
    
    vectorstore = load_vectorstore(DB_DIR)
    chain = build_qa_chain(vectorstore)
    
    print(f"\n❓ 问题：{question}")
    print("-" * 40)
    answer = ask(chain, question)
    print(f"💬 回答：{answer}")


def cmd_chat():
    """多轮对话模式"""
    if not os.path.exists(DB_DIR):
        print("❌ 还没有建立索引，请先用 load 命令加载文档")
        return
    
    vectorstore = load_vectorstore(DB_DIR)
    chain = build_qa_chain(vectorstore)
    
    print("\n🤖 进入对话模式（输入 quit 退出）")
    print("-" * 40)
    
    while True:
        try:
            question = input("\n你：").strip()
            if question.lower() in ("quit", "exit", "q", "退出"):
                print("👋 再见！")
                break
            if not question:
                continue
            
            answer = ask(chain, question)
            print(f"\n助手：{answer}")
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "load":
        if len(sys.argv) < 3:
            print("用法：python main.py load <文件路径>")
            return
        cmd_load(sys.argv[2])
    
    elif command == "ask":
        if len(sys.argv) < 3:
            print("用法：python main.py ask <问题>")
            return
        cmd_ask(" ".join(sys.argv[2:]))
    
    elif command == "chat":
        cmd_chat()
    
    else:
        print(f"未知命令：{command}")
        print(__doc__)


if __name__ == "__main__":
    main()
