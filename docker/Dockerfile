# ===== 阶段 1: 从官方 Node 镜像获取二进制文件 =====
FROM node:20-slim AS node_source

# ===== 1. 基础镜像 =====
FROM python:3.12-slim-bookworm

# ===== 2. 基础环境变量 =====
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

# ===== 3. 设置工作目录 =====
WORKDIR /app

# ===== 4. 配置 Debian 国内镜像源 =====
RUN rm -rf /etc/apt/sources.list.d/* && \
  echo "\
    deb https://mirrors.ustc.edu.cn/debian bookworm main contrib non-free non-free-firmware\n\
    deb https://mirrors.ustc.edu.cn/debian bookworm-updates main contrib non-free non-free-firmware\n\
    deb https://mirrors.ustc.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware\n\
    " > /etc/apt/sources.list

# ===== 5. 系统依赖 =====
# RUN apt-get clean && apt-get update --fix-missing && apt-get install -y --fix-missing\
#     build-essential \
#     git \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get clean  && apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 3. *** 关键步骤：直接从 node 镜像拷贝 node 和 npm ***
COPY --from=node_source /usr/local/bin /usr/local/bin
COPY --from=node_source /usr/local/lib /usr/local/lib

# 安装 MCP Filesystem Server (全局安装) =====
# 使用 npm 全局安装，并确保安装过程不会因为权限问题报错
RUN npm install -g @modelcontextprotocol/server-filesystem

# ===== 6. 安装 uv =====
RUN pip install --no-cache-dir uv

# ===== 7. 拷贝依赖声明文件（利用 Docker 缓存）=====
COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

# ===== 8. 安装第三方依赖 (使用 --system 标志) =====
# 即使设置了 UV_SYSTEM_PYTHON=1，建议显式指定安装到系统，避免 uv 创建 .venv
RUN uv pip install --system --requirement pyproject.toml
# 确保 PATH 包含虚拟环境
ENV PATH="/app/.venv/bin:$PATH"

# ===== 9. 复制项目文件 =====
COPY . .

# ===== 10. 创建输出目录 =====
RUN mkdir -p generated_projects

# ===== 11. 启动命令 =====
# 使用 uv run 会自动寻找并激活虚拟环境中的依赖
CMD ["python", "simple_mcp_angent.py"]