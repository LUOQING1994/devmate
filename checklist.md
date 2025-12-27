# AI 编程面试项目: 交互与评估清单

本清单旨在指导候选人完成开发过程，并协助面试官评估 "DevMate" 项目。

## 第一阶段: 环境与基础

- [ ] **项目设置**:
  - [ ] 创建一个新的项目目录。
  - [ ] **Git 初始化**: 初始化 git 仓库，并关联到 GitHub 远程仓库。
  - [ ] **环境管理 (关键)**: 使用 `uv` 进行项目初始化和虚拟环境管理。
    - [ ] **注意**: 必须使用 `uv`。如果发现未使用 `uv`，视为考核不通过。
  - [ ] **Python 版本**: 确保项目配置为使用 Python 3.13。
  - [ ] **依赖安装**: 安装 `langchain>=1.1.0` (确保使用 1.x 系列的最新版本)。
  - [ ] **模型来源 (如适用)**: 如果使用开源模型，验证其是否可从 HuggingFace, ModelScope, 或 Ollama 获取。
- [ ] **配置管理**:
  - [ ] 创建 `.env` 或 `config.toml` 文件。
  - [ ] **必须包含的变量**:
    - `AI_BASE_URL`: 模型 API 的基础 URL。
    - `API_KEY`: 鉴权密钥。
    - `TAVILY_API_KEY`: Tavily 搜索服务的 API 密钥。
    - `MODEL_NAME` / `EMBEDDING_MODEL_NAME` 等: **所有**涉及的模型名称都必须暴露配置项。如果使用了多个不同的模型（例如一个用于规划，一个用于生成），它们必须分别可配置。
    - `LANGCHAIN_TRACING_V2` / `LANGCHAIN_API_KEY`: LangSmith 相关配置（或其他可观测性工具配置）。
  - [ ] **代码实现**:
    - [ ] 确保代码通过读取这些环境变量来初始化 LLM 和 Embedding 客户端，而不是硬编码。
    - [ ] **关键检查**: 确认代码中使用了 `ChatOpenAI` 或 `ChatDeepSeek` 类来初始化 LLM。
  - [ ] 确保 `.gitignore` 排除带有敏感信息的配置文件。

## 第二阶段: MCP 实现 (网络搜索)

- [ ] **MCP Server**:
  - [ ] 实现一个基本的 MCP server，暴露 `search_web` 工具。
  - [ ] **工具实现**: 必须集成 **Tavily Search API**。
  - [ ] 验证 server 正常运行并监听 stdio 或 SSE。
- [ ] **MCP Client**:
  - [ ] 在主应用程序中实现一个 MCP client。
  - [ ] 将 client 连接到 MCP server。
  - [ ] **测试**: 运行手动测试，确保 Agent 成功调用搜索工具并返回结果。

## 第三阶段: RAG 实现 (文档检索)

- [ ] **数据摄入**:
  - [ ] 创建 `docs/` 文件夹并添加一些模拟 markdown 文件 (例如 "internal_fastapi_guidelines.md")。
  - [ ] 实现脚本以读取并切分这些文件。
- [ ] **向量数据库**:
  - [ ] 初始化本地向量存储 (Chroma/FAISS/Simple)。
  - [ ] 生成切片的嵌入 (Embeddings) 并存储。
- [ ] **检索工具**:
  - [ ] 创建函数/工具 `search_knowledge_base(query)` 查询向量数据库。
  - [ ] **测试**: 验证查询 "project guidelines" 能返回模拟文件的内容。

## 第四阶段: Agent 核心

- [ ] **Agent 循环**:
  - [ ] 实现接受用户输入的主 Agent 循环。
  - [ ] 将 `search_web` (通过 MCP) 和 `search_knowledge_base` (本地工具) 集成到 Agent 的工具集中。
  - [ ] **可观测性集成 (关键)**:
    - [ ] 配置 LangSmith 或 LangFuse 等追踪工具。
    - [ ] **注意**: 必须集成可观测性工具。如果未集成，视为考核不通过。
    - [ ] **测试**: 运行一次对话，确保能在后台看到完整的 Trace（包括工具调用参数和结果）。
- [ ] **提示词工程 (Prompt Engineering)**:
  - [ ] 设计系统提示词，指示 Agent 在构建新服务时检查 *网络* 和 *本地文档*。
  - [ ] 确保 Agent 知道如何生成文件内容 (例如输出带有文件名的代码块)。

## 第五阶段: 端到端场景 ("徒步路线网站测试")

- [ ] **执行**:
  - [ ] 运行 Agent。
  - [ ] 输入: "我想构建一个展示附近徒步路线的网站项目。"
- [ ] **评估**:
  - [ ] **观察**: Agent 是否搜索了网络？ (检查日志/输出)。
  - [ ] **观察**: Agent 是否搜索了本地文档？ (检查日志/输出)。
  - [ ] **结果**: 是否生成了文件？ (`main.py`, `pyproject.toml` 等)。
  - [ ] **质量**:
    - `main.py` 看起来正确吗？
    - 它是否反映了模拟文档中隐藏的任何 “内部指南”？ (加分项)。

## 第六阶段: Docker 集成 (DevMate 本身)

- [ ] **容器化**:
  - [ ] 编写 `Dockerfile` 以构建 DevMate 应用镜像。
  - [ ] 编写 `docker-compose.yml` 编排服务 (App + Vector DB + MCP Server)。
- [ ] **构建与运行**:
  - [ ] **测试**: 运行 `docker compose up`。
  - [ ] **验证**: 在容器内，Agent 依然可以正常访问网络 (MCP Search) 和读取向量库 (RAG)。
  - [ ] **验证**: 确保文件生成功能在容器挂载的卷 (Volume) 中正常工作。

## 第七阶段: 代码审查与润色

- [ ] **代码质量**:
  - [ ] 代码是否模块化？ (关注点分离: Agent vs. Tools vs. DB)。
  - [ ] 是否有错误处理？ (如果搜索失败怎么办？)。
- [ ] **文档**:
  - [ ] 是否有 `README.md` 解释如何运行项目？

## 第八阶段: 交付

- [ ] **GitHub 提交**:
  - [ ] 确保所有代码已推送到 GitHub。
  - [ ] 检查提交历史是否清晰。
  - [ ] 提交仓库链接。
