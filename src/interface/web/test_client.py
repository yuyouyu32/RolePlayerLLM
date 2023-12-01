import asyncio
import websockets

async def websocket_client():
    async with websockets.connect("ws://localhost:8085/ws") as websocket:
        message = "谁有禁疗技能"
        print(f"Sending: {message}")
        await websocket.send(message)

        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.get_event_loop().run_until_complete(websocket_client())
