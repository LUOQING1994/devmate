# DevMate 🤖

**AI-Powered Development Assistant (Interview Project)**

## 📌 项目简介

**DevMate** 是一个基于大语言模型（LLM）的智能编程助手，旨在帮助开发者根据自然语言需求：

- 自主搜索网络信息（基于 **Model Context Protocol, MCP**）
- 检索本地知识库（基于 **RAG**）
- 规划并生成真实、可运行的项目代码结构

本项目重点体现以下能力：

- Agent 系统设计
- MCP 工具调用
- RAG（检索增强生成）
- 工程化能力（配置管理、可观测性、Docker 化）

## 🧱 当前阶段说明（Stage 0）

> **当前状态：项目骨架已完成，进入核心功能实现前的准备阶段**

截至目前，本仓库已完成：

- ✅ 使用 **uv** 初始化项目（Python 3.13）
- ✅ 设计并创建完整、可扩展的项目目录结构
- ✅ 明确区分 Agent、工具、RAG、MCP Server 等模块职责
- ✅ 预留 Docker、RAG、本地文档、生成项目目录
- ✅ 完成 Git 初始化与首次提交

> 后续功能将基于该结构 **逐步迭代实现**，每一步均保持可运行、可回滚。

## 📂 项目目录结构说明

```text
devmate/
├── pyproject.toml            # uv 项目配置（Python 3.13 + 依赖）
├── uv.lock                   # uv 锁文件
├── README.md                 # 项目说明（本文档）
├── .env.example              # 环境变量示例（不包含敏感信息）
├── .gitignore
├── backend/                  # 后端服务
│       └── router            # FastApi路由
│       └── services          # 服务层
│       └── tools             # 工具
├── docker/                   # Docker 相关文件
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/                     # RAG 本地知识库（Markdown 文档）
│
├── scripts/                  # 辅助脚本（如文档摄入）
│   └── ingest_docs.py
│
├── mcp_server/               # MCP Server（网络搜索）
│   ├── server.py
│   └── tavily_client.py
│
├── devmate/                  # 主应用包
│   │
│   ├── agent/                # Agent 核心逻辑
│   │   ├── core.py
│   │   └── prompts.py
│   │
│   ├── tools/                # Agent 可调用工具
│   │   ├── mcp_search.py
│   │   └── rag_search.py
│   │
│   ├── rag/                  # RAG 向量检索相关
│   │   ├── vectorstore.py
│   │   └── embeddings.py
│   │
│   ├── llm/                  # LLM 客户端初始化
│   │   └── client.py
│   │
│   ├── config/               # 配置管理（Anget连接池）
│   │   └── agent_config.py
│   │   └── agent_pool.py
│   │
│   └── filesystem/           # 文件系统操作（生成项目）
│   │   └── writer.py
│   └── prompts/              # Agent 提示词
│       └── program_prompt.txt
│
├── generated_projects/       # Agent 生成的项目输出目录
└── web/                      # 前端服务
```
## 👈 DevMate智能体流程

```text
用户输入  
   ↓  
📚 **RAG 本地检索（带来源）**  
   ↓  
🔍 **MCP 网页搜索**  
   ↓  
🧠 **统一上下文摘要器**
   ↓  
📄 **结构化上下文（带来源）**
   ↓  
💬 **最终流式回答**
```
## 🧠 设计原则

本项目在设计上遵循以下原则：

- **关注点分离**：Agent 决策、工具能力、模型调用、I/O 操作严格解耦，便于维护与测试。
- **配置优先**：所有模型、API Key、服务地址均通过环境变量配置，避免硬编码。
- **渐进式交付**：每一个阶段都保证代码结构清晰、可运行、可追溯（Git Commit）。
- **跨平台兼容**：本地开发环境为 Windows，代码实现中统一使用 pathlib，确保在 Linux / Docker 环境中正常运行。

## 🚀 后续计划（Roadmap）

接下来的实现将按以下顺序进行：

- [X] **Iteration 1**：项目骨架搭建
- [X] **Iteration 2**：最小可运行 Agent（LLM + CLI）
  - 整合基于FastApi的前后端Websockt服务。添加**Agent连接池**，以提高项目的并发。
  - 重构部分项目框架，实现前端、后端、Agent端的**三端分离**。
- [X] **Iteration 3**：MCP Server + 网络搜索（Tavily）
  - 显示调用MCP的联网服务，为防止查询的内容过多导致token不可控，单独实现了**查询内容摘要总结Agent**。
- [X] **Iteration 4**：RAG 文档检索（本地知识库）
  - 为本地知识库召回的数据和联网查询的数据 构建了一个内容摘要总结的Agent，**减少内容冲突、去除重复内容、提高数据质量**
- [ ] **Iteration 5**：多文件项目生成能力
- [ ] **Iteration 6**：Docker 化与端到端验证
