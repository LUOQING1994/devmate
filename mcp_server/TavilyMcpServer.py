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
from tavily import TavilyClient

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
            formatted_list = []
            for r in results:
                formatted_list.append({
                    "title": r.get("title", "无标题"),
                    "url": r.get("url", ""),
                    "content": r.get("content", "")[:500]
                })
            json_text = json.dumps(formatted_list, ensure_ascii=False, indent=2)
            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=json_text
                    )
                ]
            )

        except Exception as e:
            print(f"[服务器] 搜索错误: {e}", file=sys.stderr)
            return {
                "content": [

                    {"type": "text", "text": f"搜索出错: {str(e)}"}

                ],
                "isError": True
            }

def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """
    Call Tavily Search API.
    """
    # client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))
    client = TavilyClient(api_key="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")

    response = client.search(
        query=query,
        max_results=max_results,
    )

    return response.get("results", [])


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