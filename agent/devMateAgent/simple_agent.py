"""
SimpleAgent：基于 LangGraph 与 DeepAgents 的轻量级对话智能体封装。

模块职责：
- 初始化并配置后端大语言模型（支持流式输出）
- 加载系统级 Prompt，用于约束智能体整体行为
- 创建具备“跨轮次记忆能力”的 Agent（基于 LangGraph Checkpointer）
- 对外提供统一、简洁的流式交互接口

设计说明：
- 使用 thread_id 对对话进行隔离，支持多用户 / 多会话场景
- Agent 的内部实现细节对调用方完全透明，便于后续演进
- 当前实现偏向工程可读性与可维护性，而非最小 Demo
"""

# ===== 标准库 =====
import os

# ===== 第三方库 =====
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from deepagents import create_deep_agent

# ===== 本地模块 =====
from utils.load_prompt import load_prompt


class SimpleAgent:
    """
    SimpleAgent 是一个面向工程实践的智能体封装类。

    该类负责：
    - 管理 LLM 初始化与配置
    - 统一 Prompt 加载入口
    - 构建带有记忆能力的 Agent 实例
    - 提供异步、流式的对话接口
    """

    def __init__(self, tools: list):
        """
        初始化 SimpleAgent。

        Args:
            tools: 智能体可使用的工具列表（如 MCP 工具、搜索工具、文件系统工具等）
        """

        # ===== 加载系统级 Prompt =====
        # 系统 Prompt 用于定义 Agent 的角色、能力边界与行为规范
        self.system_prompt = load_prompt("program_prompt.txt")

        # ===== 从环境变量中读取 LLM 配置 =====
        # 这样做可以避免将敏感信息硬编码在代码中
        self.llm_api_key = os.getenv("API_KEY", "")
        self.llm_base_url = os.getenv("AI_BASE_URL", "")
        self.llm_model_name = os.getenv("MODEL_NAME", "")

        # ===== 初始化大语言模型 =====
        # 启用 streaming 以支持实时输出
        self.model = ChatOpenAI(
            model=self.llm_model_name,
            api_key=self.llm_api_key,
            base_url=self.llm_base_url,
            temperature=0.8,
            streaming=True,
        )

        # ===== 初始化记忆存储（Checkpoint） =====
        # 在 LangGraph 中，记忆通过 checkpointer 实现
        # InMemorySaver 适合本地调试或 Demo 场景
        self.memory = InMemorySaver()

        # ===== 创建智能体实例 =====
        # DeepAgent 会自动将模型、工具和记忆整合到执行图中
        self.agent = create_deep_agent(
            model=self.model,
            tools=tools,
            system_prompt=self.system_prompt,
            checkpointer=self.memory,
        )

        # ===== Agent 执行配置 =====
        # thread_id 用于区分不同对话线程，是“记忆隔离”的关键
        self.config = {"configurable": {"thread_id": "user_123"}}

    async def stream(self, user_input: str):
        """
        以流式方式与智能体进行交互。

        Args:
            user_input: 用户输入的自然语言文本

        Yields:
            智能体在推理与生成过程中的实时输出结果
        """

        # 构造符合 LangGraph 规范的输入结构
        input_payload = {
            "messages": [
                {
                    "role": "user",
                    "content": user_input,
                }
            ]
        }

        # 以流式方式执行 Agent
        async for chunk in self.agent.astream(
            input_payload,
            self.config,
            stream_mode="values",
        ):
            # pretty_print 主要用于开发与调试阶段，
            # 生产环境中可替换为日志或前端事件推送
            chunk["messages"][-1].pretty_print()
