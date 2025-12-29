import os
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient  


#  测试MCP是否连接上

# 1. 设置 API 密钥（以 OpenAI 为例）
API_KEY = "514eb62a-12aa-4fbe-b162-85602ec259a5"
AI_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
MODEL_NAME = "ep-20251209172119-s5sqx"


async def main():
        
    client = MultiServerMCPClient(  
        {
            "math": {
                "transport": "stdio",  # Local subprocess communication
                "command": "python",
                # Absolute path to your math_server.py file
                "args": ["mcp_server/server.py"],
            }
        }
    )
    tools = await client.get_tools() 
    # 3. 初始化模型
    # create_agent 支持直接传入模型名称字符串或模型实例
    model = ChatOpenAI(
                model = MODEL_NAME,
                api_key = API_KEY,
                base_url = AI_BASE_URL,
                temperature = 0.8,
                streaming = True
            )

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

    print("--- 第一轮对话 ---")
    input_1 = {"messages": [{"role": "user", "content": "使用搜索工具查询广州东莞市周围的徒步路线"}]}
    async for chunk in agent.astream(input_1, config, stream_mode="values"):
        chunk["messages"][-1].pretty_print()

import asyncio
import sys

if __name__ == "__main__":

    # 简单的服务器健康检查
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("[服务器] 服务器被中断", file=sys.stderr)
    except Exception as e:
        print(f"[服务器] 服务器错误: {e}", file=sys.stderr)
        sys.exit(1)