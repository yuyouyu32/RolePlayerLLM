import websockets
import asyncio
from .model import Model
from .config import *
import json

async def process_requests(request_queue):
    model = Model() 
    while True:
        if not request_queue.empty():
            try:
                websocket, message = await request_queue.get()
                #print("qsize {}".format(request_queue.qsize()))
                #print(f"Processing received message: {message}")
                message = json.loads(message)
                if 'generation_config' in message:
                    response = model.predict(prompt=message['instruction'], system_prompt=message['system_prompt'], histories=message['histories'], generation_config=message['generation_config'])
                else:
                    response = model.predict(prompt=message['instruction'], system_prompt=message['system_prompt'], histories=message['histories'])
                #print("send..")
                await websocket.send(response)
                await websocket.close()
                #print("process end..")
            except Exception as e:
                print(e)
        else:
            await asyncio.sleep(0.3)

async def handle_websocket_request(websocket, path, request_queue):
    async for message in websocket:
        print(f"Received: {message}")
        await request_queue.put((websocket, message))
        print("qsize {}".format(request_queue.qsize()))

async def main():
    request_queue = asyncio.Queue()

    # Create a background task to process requests
    background_task = asyncio.create_task(process_requests(request_queue))

    # Start the server
    server = await websockets.serve(
        lambda websocket, path: handle_websocket_request(websocket, path, request_queue),
        MODEL_SERVER_IP,
        MODEL_SERVER_PORT
    )

    print("WebSocket server started")
    await server.wait_closed()

    # Cancel the background task
    background_task.cancel()
    await background_task

if __name__ == "__main__":
    asyncio.run(main())
