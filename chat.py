from dotenv import load_dotenv
import asyncio
import json
from openai import OpenAI
from langsmith.wrappers import wrap_openai
load_dotenv()  # 自动加载 .env 文件中的变量


# --- 2. 包装客户端以实现自动追踪 ---
# 使用 wrap_openai 后，所有通过 client 发起的调用都会自动同步到 LangSmith
client = wrap_openai(OpenAI())

# --- 3. 工具定义 ---
def get_weather(city: str) -> str:
    """获取指定城市的实时天气。"""
    print(f"  [系统日志] 正在执行本地工具: get_weather('{city}')...")
    # 模拟返回
    return f"{city}的天气是：晴转多云，气温 18°C，建议穿长袖。"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的实时天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"}
                },
                "required": ["city"],
            },
        },
    }
]

# --- 4. Agent 核心逻辑 ---
async def run_weather_agent(question: str):
    messages = [
        {"role": "system", "content": "你是一个专业的天气助手。"},
        {"role": "user", "content": question}
    ]

    # 第一轮：模型判断是否需要工具
    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=messages,
        tools=tools,
    )

    curr_message = response.choices[0].message
    
    if curr_message.tool_calls:
        messages.append(curr_message)
        
        for tool_call in curr_message.tool_calls:
            args = json.loads(tool_call.function.arguments)
            # 执行工具
            result = get_weather(args.get("city"))
            
            # 反馈结果
            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": "get_weather",
                "content": result,
            })
        
        # 第二轮：模型汇总结果给出最终回答
        final_response = client.chat.completions.create(
            model="glm-4.7-flash",
            messages=messages,
        )
        return final_response.choices[0].message.content
    
    return curr_message.content

async def main():
    print("使用GLM-4.7-Flash模型")
    user_input = "我现在在北京，出门需要穿短袖吗？"
    
    answer = await run_weather_agent(user_input)
    
    print("\n" + "="*20)
    print(f"最终建议: {answer}")
    print("="*20)
    print("\n[提示] 搜索完成！")

if __name__ == "__main__":
    asyncio.run(main())