import websockets
from typing import Tuple, List, Any, Dict
import json
import asyncio
from agent.vector_source.document import Document
from sentence_transformers import SentenceTransformer
from .config import *

class Vectorizor():
    def __init__(self, config: Dict[str, Any]):
        model_path = config["path"]
        self.m = SentenceTransformer(model_path)

    def vectorize(self, sentence: str):
        sentence_embeddings = self.m.encode(sentence)
        return sentence_embeddings

async def process_requests(request_queue: asyncio.Queue, embedding_name: str, config: Dict[str, Any]):
    """
    Describtion:
        Process knowledge base search requests from the queue
    Input:
        request_queue: request queue for search task from client
        embedding_name: name of the embedding model
    """
    print("load model..")
    vectorizor = Vectorizor(config)
    print("load model end.")
    while True:
        if not request_queue.empty():
            try:
                websocket, req = await request_queue.get()
                parsed_response = json.loads(req)
                sentence = parsed_response["sentence"]
                embedding = vectorizor.vectorize(sentence)
                #print("====================================")
                #print(f"embedding_name: {embedding_name}")
                #print(f"embedding: {embedding}")
                #print("====================================")
                rsp = {"embedding": embedding.tolist()}
                await websocket.send(json.dumps(rsp))
                await websocket.close()
            except Exception as e:
                print(e)
        else:
            await asyncio.sleep(0.3)

async def handle_websocket_request(websocket, path, request_queue):
    async for message in websocket:
        print(f"Received: {message}")
        await request_queue.put((websocket, message))

def create_wrapped_handler(request_queue):
    async def wrapped_handle_request(websocket, path):
        return await handle_websocket_request(websocket, path, request_queue)
    return wrapped_handle_request

async def main():
    servers = []
    background_tasks = []

    for embedding_name, config in embedding_config.items():
        request_queue = asyncio.Queue()

        background_task = asyncio.create_task(process_requests(request_queue, embedding_name, config))
        background_tasks.append(background_task)

        # Create a closure function to handle request
        wrapped_handle_request = create_wrapped_handler(request_queue)

        server = await websockets.serve(
            wrapped_handle_request,
            config["ip"],
            config["port"]
        )
        print(f"WebSocket server for {embedding_name} started on port {config['port']}")
        servers.append(server)

    await asyncio.gather(*(server.wait_closed() for server in servers))
    await asyncio.gather(*background_tasks)


if __name__ == "__main__":
    asyncio.run(main())
