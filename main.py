from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

# 加载 .env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
from backend.router.ws_router import router as ws_router

app = FastAPI(title="DevMate Agent")

app.mount(
    "/ui",
    StaticFiles(directory="web/static", html=True),
    name="ui",
)

app.include_router(ws_router)

# ⭐ 关键部分 —— 支持 python main.py 直接运行 uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",           # 引用本文件的 app 实例
        host="0.0.0.0",
        port = 8008,
        reload = False,           # 热重载
        workers = 1
    )
