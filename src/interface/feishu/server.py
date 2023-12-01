from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from util.session import Session
from agent.agent import Agent
from .config import SERVER_PORT
import json
import atexit

app = FastAPI()
bot = Agent()

async def bot_handler(websocket: WebSocket):
    """
    receive message from client and send response
    message:
    {
        "session": {
            "user_id": "ou_3542842ffa3d2f034da611e3e0045c44",
            "user_name": "志凯",
            "prototype_id": "kuma",
            "pair_id": "ou_3542842ffa3d2f034da611e3e0045c44_kuma",
            "agent_id": "ou_3542842ffa3d2f034da611e3e0045c44_kuma"
            
            },
        "observation": {
            "query": "你喜欢我吗",
            "time": "2023-09-27 08:25:19.015570",
            "interact": "你被志凯打了一下",
            },
        "action_type": "chat",
    }
    """
    message = await websocket.receive_text()
    message = json.loads(message)

    session_config = message['session']
    session = Session(**session_config)
    config = message['config']
    
    bot.set_bot(config, session)
    if message['action_type'] not in bot.methods:
        await websocket.send_text("Action type not supported!")
        return
    bot.session_init()
    observation = message['observation']
    print(f"process {message}")
    rsp = json.dumps(bot.methods[message['action_type']](observation), ensure_ascii=False)
    print(rsp)
    await websocket.send_text(rsp)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        await bot_handler(websocket)
    except WebSocketDisconnect:
        print("WebSocket disconnected")

def del_bot():
    global bot
    del bot
    # Session.save_sessions_to_file()


if __name__ == '__main__':
    import uvicorn
    # Session.load_sessions_from_file()
    uvicorn.run(app, host="127.0.0.1", port=SERVER_PORT)
    atexit.register(del_bot)
