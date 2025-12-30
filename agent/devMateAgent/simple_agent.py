
import os
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

from langgraph.checkpoint.memory import InMemorySaver
from utils.load_prompt import load_prompt

class SimpleAgent():

    def __init__(self, tools):
        #  == 提示词 =================
        program_prompts = load_prompt("program_prompt.txt")
        #  ==========================
        
        #  == 对话模型秘钥基础配置 =================
        llm_model_key = os.getenv("CODE_MODEL_KEY", "")
        llm_api_base_url = os.getenv("CODE_LLM_BASE_URL", "")
        llm_model = os.getenv("CODE_LLM_NAME", "")

        # 初始化后端大模型
        model = ChatOpenAI(
            model = llm_model,
            api_key = llm_model_key,
            base_url = llm_api_base_url,
            temperature = 0.8,
            streaming = True
        )
        
        # 创建记忆存储 (Memory/Persistence)
        # 在最新的 LangChain 中，通过 checkpointer 实现跨轮次记忆
        memory = InMemorySaver()
        
        # 5. 创建智能体 (Agent)
        # 这是最新文档推荐的简化写法
#         program_prompts = """使用python生成一个冒泡排序，生成的代码文件已sord.py命名。并调用 'filesystem' 保持到本地磁盘。
#         ## 工具说明
#         filesystem: 
#         1. **项目规划**：首先向用户简述你的项目结构设计。
#         2. **创建目录**：使用 'create_directory' 工具，按照查询得到的规范，预先创建所有必要的文件夹。
#         3. **写入文件**：使用 'write_file' 工具将代码写入对应的路径。
#         - 在调用 write_file 时，请直接使用相对路径（如 sore.py 或 src/main.js），严禁在路径开头添加斜杠 / 或盘符 C:
#         - 只能使用相对路径。禁止在路径开头使用正斜杠 / 或反斜杠 \。
#         - 严禁在对话框中直接输出大段 Markdown 代码块，除非用户明确要求预览。
#         - 所有的 JS/HTML/Python 代码必须保证语法正确，CSS 必须符合样式规范。
#         - 每次写入文件后，请简要说明该文件的用途。
#         - 严禁幻觉！如果没有调用 write_file 工具并收到成功的返回，绝对不允许向用户报告“已保存”。
#         - 如果工具返回 'Error'，你必须如实告知用户错误原因。
#         4. 请始终使用相对于根目录的路径。例如：
#         - 错误写法：path="/sort.py" 或 path="F:/.../sort.py"
#         5. 如果你需要创建子文件夹，请先调用 create_directory(path="src")，然后调用 write_file(path="src/main.js")。
#    """
        self.agent = create_deep_agent(
            model=model,
            tools=tools,
            system_prompt= program_prompts,
            checkpointer = memory
        )
        
        # 6. 运行智能体并测试记忆功能
        # 我们通过 thread_id 来区分不同的对话线程（即“记忆”的索引）
        self.config = {"configurable": {"thread_id": "user_123"}}
     
    async def stream(self, user_input: str):

        input_obj = {"messages": [{"role": "user", "content": user_input }]}
        
        async for chunk in self.agent.astream(input_obj, self.config, stream_mode="values"):
            chunk["messages"][-1].pretty_print()

            