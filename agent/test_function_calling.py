import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from tools import ALL_TOOLS, TOOL_FUNCTIONS, execute_tool

load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://api.deepseek.com",
)


# ============================================================
# 测试函数
# ============================================================

def test_weather_intent():
    """测试天气查询"""
    print("\n" + "=" * 40)
    print("测试天气查询")
    print("=" * 40)
    
    user_input = "北京今天的天气怎么样？"
    print(f"👤 用户：{user_input}")
    print("-" * 40)

    messages = [{"role": "user", "content": user_input}]

    from tools import weather_tool
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
        messages=messages,
        tools=[weather_tool],
        tool_choice="auto",
    )

    message = response.choices[0].message

    if message.tool_calls:
        # 处理每个工具调用
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"🔧 调用工具：{tool_name}")
            print(f"📦 参数：{arguments}")
            print("-" * 40)

            result = execute_tool(tool_name, arguments)
            print(f"🌤️ 工具返回结果：{result}")
            print("-" * 40)

            # ✅ 关键修复：先把 assistant 消息追加到 messages
            messages.append(message)
            # 然后追加对应的 tool 响应
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        # 所有工具调用完成后，请求最终回答
        final_response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
            messages=messages,
        )
        print(f"💬 最终回答：{final_response.choices[0].message.content}")
    else:
        print(f"ℹ️ 模型直接回答：{message.content}")


def test_sql_intent():
    """测试 SQL 查询"""
    print("\n" + "=" * 40)
    print("测试 SQL 数据库查询")
    print("=" * 40)
    
    user_input = "帮我查一下北京地区7月份的销售数据"
    print(f"👤 用户：{user_input}")
    print("-" * 40)

    messages = [{"role": "user", "content": user_input}]

    from tools import sql_tool, schema_tool
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
        messages=messages,
        tools=[schema_tool, sql_tool],
        tool_choice="auto",
    )

    message = response.choices[0].message

    if message.tool_calls:
        # ✅ 关键修复：先把 assistant 消息追加到 messages（只追加一次）
        messages.append(message)
        
        # 然后遍历所有 tool_calls，逐个执行并追加 tool 响应
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"🔧 调用工具：{tool_name}")
            print(f"📦 参数：{arguments}")
            print("-" * 40)

            result = execute_tool(tool_name, arguments)
            print(f"📊 工具返回：{result}")
            print("-" * 40)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        final_response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
            messages=messages,
        )
        print(f"💬 最终回答：{final_response.choices[0].message.content}")
    else:
        print(f"ℹ️ 模型直接回答：{message.content}")


def test_multi_tool():
    """测试多个工具组合（天气 + SQL）"""
    print("\n" + "=" * 40)
    print("测试多工具组合")
    print("=" * 40)
    
    user_input = "北京天气怎么样？顺便查一下北京地区7月份的销售额"
    print(f"👤 用户：{user_input}")
    print("-" * 40)

    messages = [{"role": "user", "content": user_input}]

    from tools import weather_tool, sql_tool, schema_tool
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
        messages=messages,
        tools=[weather_tool, schema_tool, sql_tool],
        tool_choice="auto",
    )

    message = response.choices[0].message

    if message.tool_calls:
        # ✅ 关键修复：先把 assistant 消息追加到 messages
        messages.append(message)
        
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print(f"🔧 调用工具：{tool_name}")
            print(f"📦 参数：{arguments}")
            print("-" * 40)

            result = execute_tool(tool_name, arguments)
            print(f"📊 工具返回：{result}")
            print("-" * 40)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        final_response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
            messages=messages,
        )
        print(f"💬 最终回答：{final_response.choices[0].message.content}")
    else:
        print(f"ℹ️ 模型直接回答：{message.content}")


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 40)
    print("🧪 Function Calling 测试套件")
    print("=" * 40)
    
    db_path = os.path.join(os.path.dirname(__file__), "sales.db")
    if not os.path.exists(db_path):
        print("\n⚠️ 数据库 sales.db 不存在，请先运行 python scripts/init_db.py 创建数据库")
    else:
        print(f"\n✅ 数据库已找到：{db_path}")
    
    test_weather_intent()
    test_sql_intent()
    test_multi_tool()