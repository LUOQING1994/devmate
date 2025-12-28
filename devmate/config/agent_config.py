from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentConfig:
    api_key: str
    api_base_url: str
    model_name: Optional[str] = None
    prompts: Optional[list] = None
