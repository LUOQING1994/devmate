import os
import asyncio
import sys
from mcp_server.McpClient import MCPClientManager
from tools.search_knowledge import query_knowledge_base
from dotenv import load_dotenv
from agent.devMateAgent.simple_agent import SimpleAgent

from log.logging_config import setup_logging
import logging
setup_logging()
logger = logging.getLogger(__name__)


# 加载 .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


async def run_my_agent():
    # 1. 定义你的配置（可选）
    my_config = {
        "search_web": {
            "transport": "stdio",
            "command": "python",
            "args": ["mcp_server/TavilyMcpServer.py"],
        }
    }

    # 2. 使用封装好的MCP类
    async with MCPClientManager(my_config) as mcp:
        # 获取联网查询的MCP工具
        tools = mcp.tools
        # 获取知识库召回工具
        logger.info("正在加载本地工具 [ 'search_knowledge_base' ]")
        tools.append(query_knowledge_base)
        logger.info("本地工具加载完毕...")
        
        user_input = "使用搜索工具查询今天的日期。通过知识库查询工具查询'Devmate是什么'。"
        devMateAgent = SimpleAgent(tools)
        await devMateAgent.stream(user_input )


if __name__ == "__main__":

    # 简单的服务器健康检查
    try:
        asyncio.run(run_my_agent())

    except KeyboardInterrupt:
        print("[服务器] 服务器被中断", file=sys.stderr)
    except Exception as e:
        print(f"[服务器] 服务器错误: {e}", file=sys.stderr)
        sys.exit(1)