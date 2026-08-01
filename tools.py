# tools.py
# 定义工具的描述，用 JSON Schema 格式

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