import os
import sqlite3
import uuid
import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from tools import ALL_TOOLS, TOOL_FUNCTIONS
from langchain_core.callbacks import StdOutCallbackHandler

load_dotenv()



# ========== 工具1：天气查询 ==========
@tool
def get_weather(city: str) -> str:
    """查询指定城市的实时天气。"""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return "错误：未配置 WEATHER_API_KEY。"

    url = "https://cn-api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_cn",
    }



    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        
        return f"{city} 当前天气：{condition}，温度 {temp}°C，湿度 {humidity}%，风速 {wind} m/s"
    
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return f"错误：未找到城市 '{city}'，请检查城市名称（尝试拼音，如 'beijing'）"
        return f"错误：天气服务 HTTP 错误 {e}"
    except Exception as e:
        return f"错误：查询天气失败 {e}"
# ========== 工具2：SQLite 数据库查询 ==========
@tool
def query_sql(sql: str) -> str:
    """
    执行 SQLite 数据库查询。
    当你需要查询销售数据、产品信息、金额统计等数据库内容时使用。
    数据库表结构：sales(id, product, category, amount, sale_date, region)
    只允许 SELECT 查询，禁止修改操作。
    """
    # 安全检查：只允许 SELECT
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return "错误：只允许执行 SELECT 查询"
    
    # 禁止危险操作
    dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "EXEC"]
    for word in dangerous:
        if word in sql_upper:
            return f"错误：禁止使用 {word} 操作"
    
    # 数据库路径（在项目根目录下）
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sales.db")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "查询结果为空"
        
        # 格式化返回结果
        result = []
        for row in rows[:50]:
            result.append(dict(row))
        
        if len(rows) > 50:
            return f"查询到 {len(rows)} 条结果（仅显示前50条）：{result}"
        
        return f"查询到 {len(rows)} 条结果：{result}"
    
    except sqlite3.OperationalError as e:
        return f"SQL 错误：{e}，请检查 SQL 语句"
    except Exception as e:
        return f"数据库查询失败：{e}"
# ========== 工具3：查看数据库表结构 ==========
@tool
def get_schema() -> str:
    """
    获取数据库的表结构信息。
    当你需要了解有哪些表、有哪些字段时，可以调用此工具。
    """
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sales.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        result = "数据库表结构：\n"
        for (table_name,) in tables:
            result += f"\n表名：{table_name}\n"
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            for col in columns:
                result += f"  - {col[1]} ({col[2]})"
                if col[3]:
                    result += " NOT NULL"
                result += "\n"
        
        conn.close()
        return result
    
    except Exception as e:
        return f"获取表结构失败：{e}"

# ========== 构建 Agent ==========
def build_agent():
    model = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL", "https://api.deepseek.com"),
        temperature=0.3,
    )

    tools = [get_weather, query_sql, get_schema]

    return create_agent(
        model=model,
        tools=tools,
        system_prompt="""你是一个智能助手，可以根据用户需求调用工具来解决问题。

你有以下工具可用：
1. get_weather：查询指定城市的实时天气
2. calculate：执行数学计算
3. query_sql：执行 SQL 查询（根据用户问题自动生成 SQL，只允许 SELECT）
4. get_schema：查看数据库表结构

当用户询问数据统计、销售额、产品信息等数据库问题时：
1. 先调用 get_schema 了解表结构
2. 根据用户问题生成合适的 SQL
3. 调用 query_sql 执行查询
4. 根据查询结果回答用户
""",
        checkpointer=InMemorySaver(),
    )


def extract_output(result: dict) -> str:
    messages = result.get("messages", [])
    if not messages:
        return "错误：模型没有返回消息。"
    content = messages[-1].content
    if isinstance(content, str):
        return content
    return str(content)


if __name__ == "__main__":
    agent = build_agent()
    config = {
    "configurable": {"thread_id": "cli-session"},
    "callbacks": [StdOutCallbackHandler()],  # 打印所有事件
}

    print("\n🤖 LangChain Agent 已启动（输入 quit 退出）")
    print("-" * 40)

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() in ["quit", "exit", "q", "退出"]:
            print("👋 再见！")
            break
        if not user_input:
            continue

        try:
            print("\n🔄 Agent 处理中...")
            print("-" * 40)
            
            # ✅ 直接用 invoke，不手动 stream
            config = {
                "configurable": {"thread_id": uuid.uuid4().hex},
                "callbacks": [StdOutCallbackHandler()],
            }
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )
            
            answer = extract_output(result)
            print(f"\n✅ 最终回答：{answer}")
                
        except Exception as error:
            print(f"\n❌ 出错：{error}")
