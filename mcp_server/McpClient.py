"""
MCPClientManager：多 MCP Server 客户端管理器。

模块职责：
- 统一管理多个 MCP Server 的生命周期
- 在异步上下文中初始化并连接 MCP Server
- 提供集中化的工具（Tool）获取入口
- 为 Agent 层屏蔽 MCP Client 的底层细节

设计说明：
- 使用 MultiServerMCPClient 同时连接多个 MCP Server
- 通过 async with 管理客户端的初始化与清理
- Filesystem MCP 的根目录被限制在指定路径内，保证文件操作安全
"""

# ===== 标准库 =====
import os
import logging
from typing import List, Any

# ===== 第三方库 =====
from langchain_mcp_adapters.client import MultiServerMCPClient

# ===== 本地模块 =====
from utils.load_prompt import find_project_root
from log.logging_config import setup_logging


# 初始化全局日志配置
setup_logging()
logger = logging.getLogger(__name__)


class MCPClientManager:
    """
    MCP 客户端管理器，用于统一管理多个 MCP Server 连接。

    该类通常作为：
    - Agent 初始化阶段的基础设施组件
    - MCP 工具的集中注册与分发入口
    """

    def __init__(self, server_config: dict | None = None):
        """
        初始化 MCPClientManager。

        Args:
            server_config: MCP Server 的配置字典。
                           若为空，则使用内置的默认配置。
        """

        # ===== 项目路径配置 =====
        # 生成代码与文件操作的安全根目录（必须为绝对路径）
        project_root = find_project_root()
        generated_projects_dir = os.path.join(project_root, "generated_projects")

        # 确保目标目录存在
        os.makedirs(generated_projects_dir, exist_ok=True)

        # ===== MCP Server 默认配置 =====
        # - mcp_server：自定义搜索 / 业务 MCP Server
        # - filesystem：官方 Filesystem MCP，用于受控文件操作
        self.server_config = server_config or {
            "mcp_server": {
                "transport": "stdio",
                "command": "python",
                "args": ["mcp_server/TavilyMcpServer.py"],
            },
            "filesystem": {
                "transport": "stdio",
                "command": "mcp-server-filesystem",
                "args": [generated_projects_dir],
            },
        }

        self.client: MultiServerMCPClient | None = None
        self._tools: List[Any] = []

    async def __aenter__(self):
        """
        进入异步上下文。

        在该阶段：
        - 初始化 MultiServerMCPClient
        - 建立与各 MCP Server 的连接
        - 预加载并缓存所有可用工具
        """

        logger.info(
            "正在启动 MCP 客户端，连接的 Server 包括: %s",
            list(self.server_config.keys()),
        )

        self.client = MultiServerMCPClient(self.server_config)

        # 预先拉取并缓存工具列表，避免后续重复请求
        self._tools = await self.client.get_tools()

        logger.info("MCP 客户端启动成功，已加载 %d 个工具。", len(self._tools))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        退出异步上下文。

        当前 MultiServerMCPClient 通常会随进程结束自动释放资源，
        但在复杂或长生命周期应用中，可在此扩展显式清理逻辑。
        """

        if self.client:
            logger.info("已退出 MCP 客户端上下文，连接已关闭。")

    @property
    def tools(self) -> List[Any]:
        """
        获取已加载的 MCP 工具列表。

        Returns:
            MCP Tool 对象列表，可直接传入 Agent 使用
        """
        return self._tools

    def get_client(self) -> MultiServerMCPClient | None:
        """
        获取底层的 MultiServerMCPClient 实例。

        该方法适用于：
        - 需要执行高级 MCP 操作
        - 绕过工具抽象直接与 MCP Server 通信的场景

        Returns:
            MultiServerMCPClient 实例，若尚未初始化则为 None
        """
        return self.client
