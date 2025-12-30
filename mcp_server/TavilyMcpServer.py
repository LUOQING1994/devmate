"""
MCP 搜索服务器（Tavily Web Search）。

模块职责：
- 通过 Model Context Protocol (MCP) 对外暴露 Web 搜索能力
- 基于 Tavily Search API 执行实时网络搜索
- 将搜索结果以 MCP 规范的 Tool Result 形式返回给客户端

设计说明：
- 采用 stdio 作为传输方式，便于与 Agent 进程进行本地通信
- 搜索逻辑通过 asyncio.to_thread 执行，避免阻塞事件循环
- 服务器本身保持无状态，适合被多个 Agent 实例复用
"""

# ===== 标准库 =====
import asyncio
import json
import os
import sys

# ===== 第三方库 =====
from tavily import TavilyClient
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from dotenv import load_dotenv
from pathlib import Path

# 1. 获取当前脚本的绝对路径
current_file_path = Path(__file__).resolve()

# 2. 找到项目的根目录 (即向上退一级): 
project_root = current_file_path.parent.parent

# 3. 拼接 .env 的绝对路径: 
env_path = project_root / ".env"

# 4. 加载环境变量
load_dotenv(dotenv_path=env_path)
# 打印一下，方便在 Docker 日志里调试（可选）
print(f"DEBUG: 正在尝试加载 .env 文件，路径: {env_path}")
print(f"DEBUG: .env 文件是否存在: {env_path.exists()}")
# ===== 创建 MCP 服务器实例 =====
server = Server("devmate-mcp-search")


@server.list_tools()
async def handle_list_tools():
    """
    返回当前 MCP Server 支持的工具列表。

    Returns:
        一个 MCP Tool 列表，用于向客户端声明可用能力。
    """
    return [
        types.Tool(
            name="search_web",
            description="使用 Tavily 搜索引擎进行网络搜索",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "需要搜索的关键词或问题"
                    }
                },
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    """
    处理 MCP Tool 调用请求。

    Args:
        name: 被调用的工具名称
        arguments: 工具调用时传入的参数

    Returns:
        MCP CallToolResult 对象，包含工具执行结果
    """

    if name != "search_web":
        return types.CallToolResult(
            isError=True,
            content=[
                types.TextContent(
                    type="text",
                    text=f"未知工具: {name}",
                )
            ],
        )

    try:
        query = arguments.get("query", "").strip()
        print(f"[MCP Server] 收到搜索请求: {query}", file=sys.stderr)

        # 使用 to_thread 将同步 IO 操作放入线程池，避免阻塞事件循环
        results = await asyncio.to_thread(search_tavily, query)

        formatted_results = [
            {
                "title": r.get("title", "无标题"),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:500],
            }
            for r in results
        ]

        json_text = json.dumps(
            formatted_results,
            ensure_ascii=False,
            indent=2,
        )

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=json_text,
                )
            ]
        )

    except Exception as exc:
        print(f"[MCP Server] 搜索执行异常: {exc}", file=sys.stderr)

        return types.CallToolResult(
            isError=True,
            content=[
                types.TextContent(
                    type="text",
                    text=f"搜索执行失败: {str(exc)}",
                )
            ],
        )


def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """
    调用 Tavily Search API 执行网络搜索。

    Args:
        query: 搜索关键词或问题
        max_results: 最大返回结果数量

    Returns:
        Tavily 搜索结果列表
    """

    api_key = os.getenv("TAVILY_API_KEY", "")
    if not api_key:
        raise RuntimeError("未配置 TAVILY_API_KEY 环境变量")

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=query,
        max_results=max_results,
    )

    return response.get("results", [])


async def main():
    """
    MCP Server 主入口。

    通过 stdio 建立通信通道，并启动 MCP Server 事件循环。
    """

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="devmate-mcp-search",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    """
    程序入口点。

    支持通过 Ctrl+C 优雅中断服务器进程。
    """

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[MCP Server] 服务器已被手动中断", file=sys.stderr)
    except Exception as exc:
        print(f"[MCP Server] 启动或运行异常: {exc}", file=sys.stderr)
        sys.exit(1)
