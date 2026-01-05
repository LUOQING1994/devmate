"""
项目路径与 Prompt 加载工具模块。

模块职责：
- 自动定位项目根目录（以特定标记文件为依据）
- 提供统一的 Prompt 加载入口，避免硬编码路径
- 支持在任意子模块中稳定读取项目资源文件

设计说明：
- 项目根目录通过向上递归查找 marker 文件确定
- Prompt 文件统一存放于 agent/prompts 目录下
- 若未找到项目根目录，将显式抛出异常，避免隐性错误
"""

# ===== 标准库 =====
import os


def find_project_root(marker: str = "pyproject.toml") -> str:
    """
    向上递归查找项目根目录。

    通过查找指定的标记文件（如 pyproject.toml），
    来确定当前文件所属的项目根路径。

    Args:
        marker: 用于标识项目根目录的文件名，默认为 pyproject.toml

    Returns:
        项目根目录的绝对路径

    Raises:
        RuntimeError: 若递归到文件系统根目录仍未找到标记文件
    """

    current_dir = os.path.abspath(os.path.dirname(__file__))

    while True:
        if os.path.exists(os.path.join(current_dir, marker)):
            return current_dir

        parent_dir = os.path.dirname(current_dir)

        # 已递归到文件系统根目录，仍未找到 marker
        if parent_dir == current_dir:
            raise RuntimeError(f"未找到项目根目录：未检测到标记文件 '{marker}'")

        current_dir = parent_dir


def load_prompt(name: str) -> str:
    """
    从项目 prompts 目录中加载指定的 Prompt 文件内容。

    Args:
        name: Prompt 文件名，例如 "program_prompt.txt"

    Returns:
        Prompt 文件的完整文本内容（字符串）

    Raises:
        FileNotFoundError: 当指定的 Prompt 文件不存在时抛出
    """

    project_root = find_project_root()
    prompts_dir = os.path.join(project_root, "agent", "prompts")
    file_path = os.path.join(prompts_dir, name)

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"未找到 Prompt 文件: {file_path}")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
