import websocket
import json
from util.decorators import cost_calculator

def _sync_websocket_client(message, ip, port):

    ws_url = "ws://{}:{}".format(ip, port)

    # 创建 WebSocket 连接
    ws = websocket.WebSocket()

    # 连接到给定的 WebSocket 服务器
    ws.connect(ws_url)

    ws.send(message)

    response = ws.recv()
    ws.close()
    return response


class ModelClient:
    def __init__(self, port: int):
        self.port = port
        self.ip = "127.0.0.1"

    @cost_calculator
    def predict(self, message: dict) -> str:
        """
        Description:
            Get the response of the LLMs model
        Input:
            prompt: the prompt to get the response
        Output:
            rsp: the response of the LLMs model
        """
        prompt_str = json.dumps(message, ensure_ascii=False)
        rsp = _sync_websocket_client(prompt_str, self.ip, self.port)
        return rsp


def unit_test():
    model = ModelClient(8725)
    response = model.predict("谁有禁疗")
    print(response)


if __name__ == "__main__":
    import time
    for i in range(3):
        t1 = time.time()
        unit_test()
        print(time.time()-t1)
