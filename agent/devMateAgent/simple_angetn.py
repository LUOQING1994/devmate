import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

# 1. 设置 API 密钥（以 OpenAI 为例）
API_KEY = "514eb62a-12aa-4fbe-b162-85602ec259a5"
AI_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_NAME = "ep-20251209172119-s5sqx"

# 3. 初始化模型
# create_agent 支持直接传入模型名称字符串或模型实例
model = ChatOpenAI(
            model = MODEL_NAME,
            api_key = API_KEY,
            base_url = AI_BASE_URL,
            temperature = 0.8,
            streaming = True
        )


# 2. 定义工具 (Tools)
# 使用 @tool 装饰器定义一个简单的工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的实时天气。"""
    # 实际应用中这里会调用天气 API
    return f"{city} 的天气是晴天，25摄氏度。"

@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积。"""
    return a * b

tools = [get_weather, multiply]



# 4. 创建记忆存储 (Memory/Persistence)
# 在最新的 LangChain 中，通过 checkpointer 实现跨轮次记忆
memory = InMemorySaver()

# 5. 创建智能体 (Agent)
# 这是最新文档推荐的简化写法
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个全能助手，可以使用工具解决问题，并记得我们的对话历史。",
    checkpointer=memory,
)

# 6. 运行智能体并测试记忆功能
# 我们通过 thread_id 来区分不同的对话线程（即“记忆”的索引）
config = {"configurable": {"thread_id": "user_123"}}

# 第一轮对话：介绍自己
print("--- 第一轮对话 ---")
input_1 = {"messages": [{"role": "user", "content": "你好，我叫小明。"}]}
for chunk in agent.stream(input_1, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# 第二轮对话：测试工具调用
print("\n--- 第二轮对话（工具调用） ---")
input_2 = {"messages": [{"role": "user", "content": "帮我查一下北京的天气，顺便算一下 12 乘以 12 等于多少？"}]}
for chunk in agent.stream(input_2, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()

# 第三轮对话：测试记忆
print("\n--- 第三轮对话（记忆测试） ---")
input_3 = {"messages": [{"role": "user", "content": "你还记得我叫什么名字吗？"}]}
for chunk in agent.stream(input_3, config, stream_mode="values"):
    chunk["messages"][-1].pretty_print()