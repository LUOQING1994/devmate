import os
import asyncio
from typing import Dict, List
from devmate.agent.program_agent import ProgramAgent
from .agent_config import AgentConfig
from devmate.prompts import load_prompt

class AgentPool:
    def __init__(self, agent_cls, config, pool_size=10):
        self.agent_cls = agent_cls
        self.config = config
        self.pool_size = pool_size
        self.pool: List = []
        self.active_count = 0  # ⭐正在被借出的数量
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            self.active_count += 1
            if self.pool:
                agent = self.pool.pop()
                agent.reset()
                return agent
            
            return self.agent_cls(self.config)

    async def release(self, agent):
        async with self._lock:
            self.active_count -= 1
            agent.reset()

            if len(self.pool) < self.pool_size:
                self.pool.append(agent)
            # 🧹 否则丢弃由 GC 回收

    def status(self):
        """提供池子状态摘要（无隐私, 无大数据）"""
        return {
            "pool_size": self.pool_size,
            "idle": len(self.pool),
            "active": self.active_count,
            "usage_rate": round(self.active_count / self.pool_size, 2)
        }

# ========= 初始化各类型 Agent 连接池 ========= #

AGENT_POOLS: Dict[str, AgentPool] = {
    "program": AgentPool(
        ProgramAgent,
        AgentConfig(
            api_keys = [os.getenv("API_KEY", ""), os.getenv("EMBEDDING_MODEL_KEY", "")],
            api_base_url = os.getenv("AI_BASE_URL", ""),
            model_names = [os.getenv("MODEL_NAME", ""), os.getenv("EMBEDDING_MODEL_NAME", "")],
            prompts= [load_prompt("program_prompt.txt"), load_prompt("search_summary_prompt.txt"), load_prompt("knowledge_prompts.txt"), load_prompt("unify_context_prompt.txt")]
        ),
        pool_size=30  # 最大 30 个 zwfw agent 并发
    )
}


async def get_agent(agent_type: str):
    pool = AGENT_POOLS.get(agent_type)
    if pool:
        return await pool.acquire()
    return None


async def return_agent(agent_type: str, agent):
    pool = AGENT_POOLS.get(agent_type)
    if pool:
        await pool.release(agent)
