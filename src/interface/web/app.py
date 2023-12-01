import json
from fastapi import FastAPI, WebSocket
from chatbot.chat_main import DislyteChatBot
from .config import APP_PORT

app = FastAPI()
chatbot = None

async def load_chatbot():
    global chatbot
    chatbot = DislyteChatBot()

@app.on_event("startup")
async def startup_event():
    """
    Describtion:
        load chatbot
    """
    await load_chatbot()

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    Describtion:
        chat with chatbot
    """
    await websocket.accept()
    data = await websocket.receive_text()
    while data is not None:
        try:
            data = json.loads(data)
            prompt = data["prompt"]
            cur_response, reference = chatbot.chat(prompt)
            await websocket.send_text(json.dumps({'response': cur_response, 'reference': reference}))
            await websocket.send_text(json.dumps({"end": True}))
            chatbot.summary()
        except Exception as e:
            await websocket.send_text(json.dumps({'error': str(e)}))
            break
        data = None

@app.websocket("/clear_memory")
async def websocket_endpoint(websocket: WebSocket):
    """
    Describtion:
        clear chatbot memory
    """
    await websocket.accept()
    data = await websocket.receive_text()
    while data is not None:
        try:
            data = json.loads(data)
            if 'clear_memory' in data and data['clear_memory']:
                chatbot.clear_memory()
                await websocket.send_text(json.dumps({'info': 'Memory cleared.'}))
        except Exception as e:
            await websocket.send_text(json.dumps({'error': str(e)}))
            break
        data = None


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=APP_PORT)
