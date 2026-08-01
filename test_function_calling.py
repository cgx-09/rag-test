import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://api.deepseek.com",  # DeepSeek 官方地址[citation:1]
)

# 1. 定义工具 (和之前一样)
weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气信息。用户需要提供一个城市名称。[citation:1]",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "城市名称，例如：北京、上海",
                }
            },
            "required": ["city"],
        },
    },
}

# 2. 定义你的真实天气查询函数
def get_real_weather(city: str) -> dict:
    """这个函数负责调用真实的天气 API"""
    # 请务必将 YOUR_WEATHER_API_KEY 替换为你在 .env 中配置的变量名
    api_key = os.getenv("WEATHER_API_KEY")  # 你需要在 .env 中配置这个 Key
    if not api_key:
        return {"error": "未配置天气 API Key，请在 .env 中设置 WEATHER_API_KEY"}

   # 使用 WeatherAPI 的实时天气接口 (更常用, 也更简单)
    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": api_key,
        "q": city,        # ✅ 修正点: WeatherAPI 使用 'q' 参数，支持中文或拼音
        "lang": "zh",     # 返回中文天气描述
    }
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        # 提取今天天气作为示例
        return {
            "city": city,
            "temperature": data["current"]["temp_c"],              # 当前温度
            "condition": data["current"]["condition"]["text"],     # 天气状况
            "humidity": data["current"]["humidity"],               # 湿度
            "wind_speed": data["current"]["wind_kph"],             # 风速 (km/h)
            "feels_like": data["current"]["feelslike_c"],          # 体感温度
            "last_updated": data["current"]["last_updated"],       # 最后更新时间
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"请求天气服务失败: {e}"}

# 3. 模拟用户提问，测试 Agent 决策
def test_weather_intent():
    print("👤 用户：北京今天的天气怎么样？")
    print("-" * 40)

    messages = [{"role": "user", "content": "北京今天的天气怎么样？"}]

    # 第一次调用：模型决定是否调用工具
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", "deepseek-v4-flash"), # 使用 V4 Flash 模型 [citation:4]
        messages=messages,
        tools=[weather_tool],
        tool_choice="auto",
    )

    message = response.choices[0].message

    # 4. 检查模型的返回
    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        city = arguments.get("city")

        print(f"🔧 模型决定调用工具：{tool_name}")
        print(f"📦 提取的参数：{arguments}")
        print("-" * 40)

        # 5. 执行真实的工具函数
        print(f"🌐 正在调用真实天气 API 查询 {city} 的天气...")
        real_result = get_real_weather(city)
        print(f"🌤️ 真实API返回结果：{real_result}")
        print("-" * 40)

        # 6. 把工具执行结果返回给模型
        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(real_result, ensure_ascii=False),
        })

        # 第二次调用：模型根据工具结果生成最终回答
        final_response = client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
            messages=messages,
        )

        print(f"💬 最终回答：{final_response.choices[0].message.content}")

    else:
        print(f"ℹ️ 模型决定不调用工具，直接回答：{message.content}")

if __name__ == "__main__":
    test_weather_intent()