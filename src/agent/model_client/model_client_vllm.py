import argparse
import json
import requests
from typing import Iterable, List

def post_http_request(prompt: str,
                      api_url: str) -> requests.Response:
    headers = {"User-Agent": "Test Client"}
    pload = {
        "prompt": prompt,
    }
    response = requests.post(api_url, headers=headers, json=pload, stream=True)
    return response


def get_response(response: requests.Response) -> List[str]:
    return response.content.decode('utf-8')

class ModelClient:
    def __init__(self, port):
        self.port = port
        self.ip = "127.0.0.1"

    def predict(self, prompt):
        api_url = f"http://{self.ip}:{self.port}/generate"
        response = post_http_request(prompt, api_url)
        rsp_txt = response.content.decode('utf-8')
        return rsp_txt

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

