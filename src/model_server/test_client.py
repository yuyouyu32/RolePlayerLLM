import asyncio
import websocket
import websockets
import json
from agent.algo_source.prompts import *

message = {
    "system_prompt": SystemPromptTemplate.format(name="毛毛", background="莉莉丝大家庭的一员，名字叫毛毛(maomao)", role_description_and_catchphrases="黑白相间的傲娇小猫，拥有黑金异瞳 说话简洁，傲娇，惜字如金"),
    "histories": [],
    "instruction": "你是大笨蛋吗？",
    "generation_config": {
                    "chat_format": "chatml",
                    "eos_token_id": 151643,
                    "pad_token_id": 151643,
                    "max_window_size": 6144,
                    "max_new_tokens": 512,
                    "do_sample": True,
                    "top_k": 0,
                    "top_p": 0.8,
                    "repetition_penalty": 1.1,
                    "transformers_version": "4.31.0"
                }
}

async def async_websocket_client(message):
    async with websockets.connect("ws://localhost:8725") as websocket:
        message = json.dumps(message, ensure_ascii=False)
        print(f"Sending: {message}")
        await websocket.send(message)

        response = await websocket.recv()
        print(f"Received: {response}")

def sync_websocket_client():
    ws_url = "ws://localhost:8725"

    # 创建 WebSocket 连接
    ws = websocket.WebSocket()

    # 连接到给定的 WebSocket 服务器
    ws.connect(ws_url)
    message = json.dumps(message)
    print(f"Sending: {message}")
    ws.send(message)

    response = ws.recv()
    print(f"Received: {response}")
    ws.close()

async def main():
    tasks = [async_websocket_client(message) for _ in range(2)]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # sync_websocket_client()
    # import time
    # for i in range(5):
    #     t1 = time.time()
    #     sync_websocket_client()
    #     print(time.time()-t1)
    #     time.sleep(1)
    asyncio.run(main())
