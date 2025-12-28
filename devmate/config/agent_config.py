from dataclasses import dataclass
from typing import Optional

@dataclass
class AgentConfig:
    api_keys: list
    api_base_url: str
    model_names: Optional[list] = None
    prompts: Optional[list] = None
