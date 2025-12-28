import json
import sys
from typing import Optional, Dict, Any, List

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPSearchClient:
    """
    即用型 MCP 搜索客户端
    """

    def __init__(
        self,
        server_command: str = "python",
        server_args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        tool_name: str = "search_web",
    ):
        self.server_params = StdioServerParameters(
            command=server_command,
            args=server_args or ["mcp_server/server.py"],
            env=env,
        )

        self.tool_name = tool_name

        self._session: Optional[ClientSession] = None
        self._stdio_cm = None
        self._session_cm = None
        self._connected = False

    # =========================
    # 内部：自动连接
    # =========================
    async def _ensure_connected(self):
        if self._connected:
            return

        print("🔌 正在连接 MCP 服务器...", file=sys.stderr)

        self._stdio_cm = stdio_client(self.server_params)
        read, write = await self._stdio_cm.__aenter__()

        self._session_cm = ClientSession(read, write)
        self._session = await self._session_cm.__aenter__()

        await self._session.initialize()

        self._connected = True
        print("✅ MCP 连接成功", file=sys.stderr)

    # =========================
    # 对外：唯一需要用的方法
    # =========================
    async def search(
        self,
        query: str,
        *,
        extra_args: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        """
        搜索并返回 title + content

        使用方式：
            result = await client.search("北京今天的天气")
        """
        await self._ensure_connected()

        arguments = {"query": query}
        if extra_args:
            arguments.update(extra_args)

        result = await self._session.call_tool(
            self.tool_name,
            arguments=arguments,
        )

        return self.extract_title_and_content_from_mcp(result)

    # =========================
    # 内部：解析 MCP 返回
    # =========================
    def extract_title_and_content_from_mcp(self, result) -> List[Dict[str, str]]:
        """
        解析当前 MCP 返回格式（双层 JSON）
        """
        final_results = []

        for content in result.content:
            if content.type != "text":
                continue

            # 第一层 JSON
            try:
                level1 = json.loads(content.text)
            except json.JSONDecodeError:
                continue

            for block in level1.get("content", []):
                datas = block.get("datas")
                if not datas:
                    continue

                # 第二层 JSON（真正的搜索结果）
                try:
                    items = json.loads(datas)
                except json.JSONDecodeError:
                    continue

                for item in items:
                    final_results.append({
                        "title": item.get("title", ""),
                        "content": item.get("content", ""),
                    })

        return final_results

    # =========================
    # 可选：手动关闭
    # =========================
    async def close(self):
        if self._session_cm:
            await self._session_cm.__aexit__(None, None, None)
            self._session_cm = None
            self._session = None

        if self._stdio_cm:
            await self._stdio_cm.__aexit__(None, None, None)
            self._stdio_cm = None

        self._connected = False
        print("🔒 MCP 连接已关闭", file=sys.stderr)
