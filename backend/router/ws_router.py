import json
import asyncio
import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from devmate.config.agent_pool import get_agent, return_agent
from backend.tools.log import write_log

        
router = APIRouter()

@router.websocket("/chat/{agent_type}")
async def websocket_agent(websocket: WebSocket, agent_type: str):
    await websocket.accept()

    agent = await get_agent(agent_type)
    if not agent:
        await websocket.send_text(json.dumps({"error": "unknown agent_type"}))
        await websocket.close()
        return

    try:
        # ⭐ 等待一次请求（不再循环）
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=10)
        msg = json.loads(raw)

        # 客户端停止请求
        if msg.get("action") == "chatStop":
            pass
                
        # -------------------------
        # 处理一次 start 请求
        # -------------------------
        user_input = msg.get("user_input")
        action = msg.get("action")
        user_id = msg.get("user_id")
        conversation_id = msg.get("conversation_id")
        
        if action == "start":
            

            if user_input == "":
                await websocket.send_text("不能输入空数据进行咨询哦~")
                return
            
            async for content in agent.stream(user_input, user_id, conversation_id):
                sse_message = f"data: {content}\n\n"
                await websocket.send_text(sse_message)
            # SSE end
            await websocket.send_text("event: end\ndata: {}\n\n")
 
    except WebSocketDisconnect:
        # -------------------------
        # 客户端提前断开：我们需要 stop dify
        # -------------------------
        pass

    except asyncio.TimeoutError:
        print("超时主动断开连接")
        
    finally:
        # ⭐无论如何都要释放 agent
        agent.reset()
        await return_agent(agent_type, agent)
        await websocket.close()
        return