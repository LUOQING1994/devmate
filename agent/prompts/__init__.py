import os

PROMPTS_DIR = os.path.join(os.path.dirname(__file__))

def load_prompt(name: str) -> str:
    file_path = os.path.join(PROMPTS_DIR, name)
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
