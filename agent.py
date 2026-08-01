import os

import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


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


def build_agent():
    model = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "deepseek-v4-flash"),
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL", "https://api.deepseek.com"),
        temperature=0.3,
    )

    return create_agent(
        model=model,
        tools=[get_weather],
        system_prompt="你是一个智能助手，可以根据用户需求调用工具来解决问题。",
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
    config = {"configurable": {"thread_id": "cli-session"}}

    print("\nLangChain Agent 已启动（输入 quit 退出）")
    print("-" * 40)

while True:
    user_input = input("\n你：").strip()
    if user_input.lower() in ["quit", "exit", "q", "退出"]:
        print("👋 再见！")
        break
    if not user_input:
        continue

    try:
        print("\n🔄 Agent 思考中...")
        print("-" * 40)
        
        final_answer = None
        for chunk in agent.stream(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config,
            stream_mode="values",
        ):
            if "messages" in chunk:
                last_msg = chunk["messages"][-1]
                
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    for tc in last_msg.tool_calls:
                        print(f"🔧 调用工具：{tc['name']}")
                        print(f"📦 参数：{tc['args']}")
                
                if hasattr(last_msg, "role") and last_msg.role == "tool":
                    content = last_msg.content[:100]
                    print(f"📊 工具返回：{content}...")
                
                if hasattr(last_msg, "role") and last_msg.role == "assistant":
                    final_answer = last_msg.content
        
        print("-" * 40)
        
        if final_answer:
            print(f"\n✅ 最终回答：{final_answer}")
        else:
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )
            print(f"\n✅ 最终回答：{extract_output(result)}")
            
    except Exception as error:
        print(f"\n❌ 出错：{error}")
