# tools.py
import os
import sqlite3
import re
import requests
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 工具1：天气查询
# ============================================================
weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "查询指定城市的天气情况",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，如：北京、上海"
                },
                "date": {
                    "type": "string",
                    "description": "查询日期，格式：YYYY-MM-DD，默认为今天"
                }
            },
            "required": ["city"]
        }
    }
}

# # ============================================================
# # 工具2：计算器
# # ============================================================
calculator_tool = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "执行数学计算",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如：2+3*4"
                }
            },
            "required": ["expression"]
        }
    }
}

# ============================================================
# 工具3：SQLite 数据库查询
# ============================================================
sql_tool = {
    "type": "function",
    "function": {
        "name": "query_sql",
        "description": """执行 SQLite 数据库的 SELECT 查询。
适用场景：查询销售数据、产品信息、金额统计、地区分析等。
数据库表结构：sales(id, product, category, amount, sale_date, region)
- product: 产品名称
- category: 品类（电子产品/家具/家电）
- amount: 销售金额
- sale_date: 销售日期（YYYY-MM-DD）
- region: 销售地区
注意：只允许 SELECT 查询，禁止修改操作。""",
        "parameters": {
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "要执行的 SQL SELECT 语句，例如：SELECT * FROM sales WHERE region='北京'"
                }
            },
            "required": ["sql"]
        }
    }
}

# ============================================================
# 工具4：查看数据库表结构
# ============================================================
schema_tool = {
    "type": "function",
    "function": {
        "name": "get_schema",
        "description": "获取数据库的表结构信息，包括所有表名、字段名、字段类型。当不确定表结构时使用。",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


# ============================================================
# 工具执行函数
# ============================================================

def get_real_weather(city: str) -> dict:
    """天气查询的执行函数（配合 OpenWeatherMap）"""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return {"error": "未配置天气 API Key"}

    url = "https://cn-api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "zh_cn"}

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
        }
    except Exception as e:
        return {"error": f"查询天气失败: {e}"}


def calculate(expression: str) -> dict:
    """计算器的执行函数"""
    try:
        # 安全校验：只允许数字和运算符
        if not re.match(r'^[\d+\-*/().\s]+$', expression):
            return {"error": "表达式包含非法字符"}
        result = eval(expression)
        return {"expression": expression, "result": result}
    except Exception as e:
        return {"error": f"计算错误: {e}"}


def query_sql(sql: str) -> dict:
    """SQL 查询的执行函数（带安全限制）"""
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return {"error": "只允许执行 SELECT 查询"}
    
    dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "EXEC"]
    for word in dangerous:
        if word in sql_upper:
            return {"error": f"禁止使用 {word} 操作"}
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sales.db")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"result": [], "count": 0}
        
        result = [dict(row) for row in rows[:50]]
        return {"result": result, "count": len(rows), "truncated": len(rows) > 50}
    except sqlite3.OperationalError as e:
        return {"error": f"SQL 错误: {e}"}
    except Exception as e:
        return {"error": f"数据库查询失败: {e}"}


def get_schema() -> dict:
    """获取表结构的执行函数"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sales.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        schema = {}
        for (table_name,) in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema[table_name] = [
                {"name": col[1], "type": col[2], "not_null": bool(col[3])}
                for col in columns
            ]
        
        conn.close()
        return {"schema": schema}
    except Exception as e:
        return {"error": f"获取表结构失败: {e}"}


# ============================================================
# 工具分发器
# ============================================================

TOOL_FUNCTIONS = {
    "get_weather": get_real_weather,
    "calculate": calculate,
    "query_sql": query_sql,
    "get_schema": get_schema,
}


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """
    统一工具执行入口
    
    Args:
        tool_name: 工具名称
        arguments: 参数字典
    
    Returns:
        dict: 执行结果或错误信息
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {"error": f"未知工具: {tool_name}，可用工具: {list(TOOL_FUNCTIONS.keys())}"}
    
    try:
        result = TOOL_FUNCTIONS[tool_name](**arguments)
        return result
    except TypeError as e:
        return {"error": f"参数错误: {e}"}
    except Exception as e:
        return {"error": f"工具执行失败: {e}"}


# ============================================================
# 工具列表（供批量注册）
# ============================================================

ALL_TOOLS = [weather_tool, calculator_tool, sql_tool, schema_tool]


# ============================================================
# 测试
# ============================================================
if __name__ == "__main__":
    print("✅ tools.py 加载成功")
    print(f"📋 已注册工具: {list(TOOL_FUNCTIONS.keys())}")
