import asyncio
from typing import List, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from utils.load_prompt import find_project_root
import os
from log.logging_config import setup_logging
import logging
setup_logging()

logger = logging.getLogger(__name__)


class MCPClientManager:
    def __init__(self, server_config: dict = None):
        """
        :param server_config: MCP 服务器配置字典
        """
        
        # 定义你希望保存代码的本地根目录（必须是绝对路径）
        PROJECT_ROOT = find_project_root()
        PROMPTS_DIR = os.path.join(PROJECT_ROOT, "generated_projects")
        if os.path.exists(PROMPTS_DIR):
            os.makedirs(PROMPTS_DIR, exist_ok=True)
            
        # 默认配置，如果外部没传则使用你提供的默认配置
        self.server_config = server_config or {
            "mcp_server": {
                "transport": "stdio",
                "command": "python",
                "args": ["mcp_server/TavilyMcpServer.py"],
            },
            "filesystem": {
            "transport": "stdio",
            "command": "mcp-server-filesystem",
                "args": [
                    PROMPTS_DIR
                ]
            }
        }
        self.client = None
        self._tools = []

    async def __aenter__(self):
        """进入异步上下文：启动连接并初始化工具"""
        logger.info(f"正在启动 MCP 客户端: {list(self.server_config.keys())}...")
        self.client = MultiServerMCPClient(self.server_config)
        # 预先获取并缓存工具列表
        self._tools = await self.client.get_tools()
        logger.info(f"MCP 客户端 启动成功!")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出异步上下文：关闭连接"""
        if self.client:
            logger.info(f"已关闭 MCP 客户端连接...")
            # 注意：MultiServerMCPClient 目前通常随进程结束释放，
            # 但在复杂应用中，建议显式处理可能的清理逻辑
            
    @property
    def tools(self) -> List[Any]:
        """返回获取到的工具列表"""
        return self._tools

    def get_client(self):
        """获取原始 client 实例以进行更高级的操作"""
        return self.client