import asyncio
import json
import websockets
from .config import SERVER_PORT

async def test_client():
    uri = f"ws://localhost:{SERVER_PORT}/ws"

    async with websockets.connect(uri) as websocket:
        # 用于测试的 JSON 数据
        json_data ={
            "session": {
            "user_id": "test_123",
            "prototype_id": "maomao",
            "user_name": "志凯"
            },
            "config": {
                "use_knowledge": True,
                "use_memory": True,
                "use_chat_history": True
                },
            "observation": {
                "source": "志凯",
                "query": "你是谁啊",
                "time": "2023-09-27 08:25:19.015570",
                "candidate_actions": ["打回去", "躲闪", "向ben求援"],
                "interact": "你被志凯打了一下",
                "world_status": "因为刮台风,今天放假不用上班"
                },
            "action_type": "ask",
    }
        

        # 将 JSON 对象转换为字符串
        json_str = json.dumps(json_data, ensure_ascii=False)

        # 向 WebSocket 服务器发送 JSON 数据
        await websocket.send(json_str)
        print(f"Sent: {json_str}")

        # 从 WebSocket 服务器接收响应并解析为 JSON 对象
        response = await websocket.recv()
        response = json.loads(response)
        content, status = response["content"], response["status"]
        print(content)
        print(json.dumps(status, ensure_ascii=False, indent=4))

asyncio.get_event_loop().run_until_complete(test_client())