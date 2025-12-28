"""

MCP 搜索服务器 (兼容 MCP 1.25.0)

"""
import json
import sys
import asyncio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from tavily_client import search_tavily
print("SERVER IMPORT OK", file=sys.stderr)

# 创建服务器实例
server = Server("devmate-mcp-search")
@server.list_tools()
async def handle_list_tools():
    # 显式返回 types.Tool 列表
    return [
        types.Tool(
            name="search_web",
            description="Search the web using Tavily search engine",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"}
                },
                "required": ["query"],
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):

    if name == "search_web":
        try:
            query = arguments.get("query", "")
            print(f"[服务器] 收到搜索请求: {query}", file=sys.stderr)
            # ✅ 关键修复点
            results = await asyncio.to_thread(search_tavily, query)
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.get("title", "无标题"),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500]
                })
                
            return {
                "content": [
                    {
                        "type": "text",
                        "datas": json.dumps(formatted, ensure_ascii=False, indent=2)
                    }
                ]
            }

        except Exception as e:
            print(f"[服务器] 搜索错误: {e}", file=sys.stderr)
            return {
                "content": [

                    {"type": "text", "datas": f"搜索出错: {str(e)}"}

                ],
                "isError": True
            }

async def main():
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
            )
        )

if __name__ == "__main__":

    # 简单的服务器健康检查
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("[服务器] 服务器被中断", file=sys.stderr)
    except Exception as e:
        print(f"[服务器] 服务器错误: {e}", file=sys.stderr)
        sys.exit(1)