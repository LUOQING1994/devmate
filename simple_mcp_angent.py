"""
DevMate Agent 主启动入口。

模块职责：
- 加载环境变量与全局日志配置
- 初始化 MCP Client（搜索 / 文件系统等工具）
- 动态组装 Agent 可用工具集合（MCP + 本地工具）
- 启动 DevMate Agent 并提供交互式对话循环

设计说明：
- MCP Client 通过 async with 管理生命周期，确保资源可控
- Agent 实例仅初始化一次，支持多轮对话与上下文记忆
- 文件系统 MCP 的访问范围被显式限制在指定目录内
"""

# ===== 标准库 =====
import os
import sys
import asyncio
import logging
from pathlib import Path

# ===== 第三方库 =====
from dotenv import load_dotenv

# ===== 本地模块 =====
from mcp_server.McpClient import MCPClientManager
from agent.devMateAgent.simple_agent import SimpleAgent
from utils.search_knowledge import search_knowledge_base
from log.logging_config import setup_logging


# ===== 日志初始化 =====
setup_logging()
logger = logging.getLogger(__name__)

# ===== 加载环境变量 =====
# 默认从当前脚本目录加载 .env 文件
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def run_my_agent() -> None:
    """
    启动 DevMate Agent 并进入交互式对话循环。

    执行流程：
    1. 构建 MCP Server 配置（搜索 + 文件系统）
    2. 启动 MCP Client Manager 并加载可用工具
    3. 初始化 Agent（仅一次）
    4. 进入多轮对话交互，支持流式输出
    """

    # ===== 1. MCP 配置 =====
    # 当前项目根目录（作为 Filesystem MCP 的安全访问边界）
    project_root = os.path.join(os.path.abspath("."), "generated_projects")

    logger.info(
        "已授权 Filesystem MCP 访问目录及其子目录: %s",
        project_root,
    )

    mcp_config = {
        "mcp_server": {
            "transport": "stdio",
            "command": "python",
            "args": ["mcp_server/TavilyMcpServer.py"],
        },
        "filesystem": {
            "transport": "stdio",
            "command": "mcp-server-filesystem",
            "args": [project_root],
        },
    }

    # ===== 2. 启动 MCP Client Manager =====
    async with MCPClientManager(mcp_config) as mcp:
        tools = mcp.tools

        # ===== 追加本地工具（RAG 检索） =====
        logger.info("正在加载本地工具: search_knowledge_base")
        tools.append(search_knowledge_base)
        logger.info("本地工具加载完成")

        # 打印并确认已加载的 MCP 工具
        for tool in tools:
            logger.info("已加载 MCP 工具: %s", tool.name)
            
        # ===== 3. 初始化 Agent（仅执行一次） =====
        devmate_agent = SimpleAgent(tools)

        print("\n🤖 DevMate Agent 已启动")
        print("👉 输入内容开始对话（输入 exit / quit 退出）\n")

        # ===== 4. 多轮对话循环 =====
        while True:
            try:
                user_input = await asyncio.to_thread(
                    input,
                    "👤 你：",
                )

                if user_input.strip().lower() in {"exit", "quit"}:
                    print("👋 已退出对话")
                    break

                if not user_input.strip():
                    continue

                # ===== 5. 调用 Agent（流式输出） =====
                await devmate_agent.stream(user_input)

            except KeyboardInterrupt:
                print("\n👋 用户中断，对话结束")
                break

            except Exception as exc:
                logger.exception("对话过程中发生异常")
                print(f"⚠️ 出现错误：{exc}")


if __name__ == "__main__":
    """
    程序主入口。

    使用 asyncio.run 启动异步事件循环，
    若启动失败则输出错误并以非零状态码退出。
    """

    try:
        asyncio.run(run_my_agent())
    except Exception as exc:
        print(f"[系统] 启动失败: {exc}", file=sys.stderr)
        sys.exit(1)
