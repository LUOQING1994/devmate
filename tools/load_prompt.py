import os

def find_project_root(marker="pyproject.toml"):
    current = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.exists(os.path.join(current, marker)):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            raise RuntimeError("Project root not found")
        current = parent

def load_prompt(name: str) -> str:
    PROJECT_ROOT = find_project_root()
    PROMPTS_DIR = os.path.join(PROJECT_ROOT, "agent/prompts")

    file_path = os.path.join(PROMPTS_DIR, name)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
