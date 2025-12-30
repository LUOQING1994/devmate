"""
日志初始化模块。

模块职责：
- 统一配置全局日志格式与输出方式
- 为控制台输出提供彩色日志，提升本地调试体验
- 避免重复添加 handler，保证日志输出可控

设计说明：
- 默认使用 StreamHandler 输出到标准输出
- 通过 colorlog 提供不同级别的颜色区分
- 该模块应在程序入口（如 main / app 启动时）调用一次
"""

# ===== 标准库 =====
import logging

# ===== 第三方库 =====
from colorlog import ColoredFormatter


def setup_logging(level: int = logging.INFO) -> None:
    """
    初始化并配置全局日志系统。

    该函数会：
    - 设置根日志器的级别
    - 清空已有的 handler，防止日志重复输出
    - 添加带颜色格式化的控制台日志 handler

    Args:
        level: 日志级别，默认为 logging.INFO
    """

    # 创建控制台日志处理器
    handler = logging.StreamHandler()

    # 设置彩色日志格式
    formatter = ColoredFormatter(
        "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )
    handler.setFormatter(formatter)

    # 获取根日志器
    root_logger = logging.getLogger()

    # 设置日志级别
    root_logger.setLevel(level)

    # 清空已有 handler，避免重复输出日志
    if root_logger.handlers:
        root_logger.handlers.clear()

    # 添加新的 handler
    root_logger.addHandler(handler)
