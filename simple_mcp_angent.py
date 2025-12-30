import os
import asyncio
import sys
from mcp_server.McpClient import MCPClientManager
from utils.search_knowledge import query_knowledge_base
from dotenv import load_dotenv
from agent.devMateAgent.simple_agent import SimpleAgent
from utils.load_prompt import find_project_root
from log.logging_config import setup_logging
from pathlib import Path

import logging
setup_logging()
logger = logging.getLogger(__name__)
# 加载 .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def run_my_agent():
    # 1. MCP 配置
    # 定义你希望保存代码的本地根目录（必须是绝对路径）
    # 获取当前 Python 脚本运行的绝对路径
    CURRENT_PROJECT_ROOT = os.path.abspath(".")

    # 建议打印出来确认一下，这就是你授权的“最高境界”
    print(f"正在授权当前目录及其所有子目录: {CURRENT_PROJECT_ROOT}")
        
    my_config = {
            "mcp_server": {
                "transport": "stdio",
                "command": "python",
                "args": ["mcp_server/TavilyMcpServer.py"],
            },
            "filesystem": {
            "transport": "stdio",
            "command": "mcp-server-filesystem",
                "args": [
                    CURRENT_PROJECT_ROOT,
                ]
            }
        }

    # 2. 启动 MCP Client Manager
    async with MCPClientManager(my_config) as mcp:
        tools = mcp.tools
        for t in tools:
            print(f"工具名: {t.name}")
        logger.info("正在加载本地工具 ['search_knowledge_base']")
        tools.append(query_knowledge_base)
        logger.info("本地工具加载完毕...")

        # 3. 初始化 Agent（只做一次）
        devMateAgent = SimpleAgent(tools)

        print("\n🤖 Agent 已启动，输入内容开始对话（输入 exit / quit 退出）\n")

        # 4. 多轮对话循环
        while True:
            try:
                user_input = await asyncio.to_thread(
                    input, "👤 你："
                )

                if user_input.strip().lower() in {"exit", "quit"}:
                    print("👋 已退出对话")
                    break

                if not user_input.strip():
                    continue

                # 5. 调用 Agent（流式）
                await devMateAgent.stream(user_input)

            except KeyboardInterrupt:
                print("\n👋 用户中断，对话结束")
                break

            except Exception as e:
                logger.exception("对话出错")
                print(f"⚠️ 出现错误：{e}")


if __name__ == "__main__":
    try:
        asyncio.run(run_my_agent())
    except Exception as e:
        print(f"[服务器] 启动失败: {e}", file=sys.stderr)
        sys.exit(1)
