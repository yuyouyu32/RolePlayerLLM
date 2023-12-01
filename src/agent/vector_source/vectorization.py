import websocket
import json
from typing import Tuple, List, Any, Dict, Union
from .document import Document

class TrsVectorizor():
    def __init__(self, config: Dict[str, Any]):
        self.ip, self.port = config["ip"], config["port"]

    def vectorize(self, sentence_info: Union[List[Document], Dict], is_query = True) -> List[float]:
        if is_query:
            sentences = [sentence_info["content"]]
        else:
            sentences = [s.content for s in sentence_info]

        sentence_embedding = self._remote_emb(sentences)
        return sentence_embedding[0] if is_query else sentence_embedding

    def _remote_emb(self, sentence: str) -> List[float]:
    
        ws_url = "ws://{}:{}".format(self.ip, self.port)
        request = {"sentence": sentence}
    
        # 创建 WebSocket 连接
        ws = websocket.WebSocket()
    
        # Connect to the server using the WebSocketClientProtocol instance.
        ws.connect(ws_url)
    
        # Send a message
        ws.send(json.dumps(request, ensure_ascii=False))
    
        # Wait for a response
        response = ws.recv()
        response = json.loads(response)
        ws.close()
        return list(response["embedding"])

def unit_test():
    from .config import embedding_config 
    for embedding_name, v in embedding_config.items():
        vectorizor =  TrsVectorizor(v)
        sentence_info = {"content": "是吧"}
        emb = vectorizor.vectorize(sentence_info, is_query = True)
        print(emb)
    for embedding_name, v in embedding_config.items():
        vectorizor =  TrsVectorizor(v)
        docs = [Document(sub_doc_id = 123,doc_id = 312,content = "{'钻石': 150}','空间之塔1-1 星级达到6，奖励为：",dtype = "new_knowledge",info = "no split"), Document(sub_doc_id = 123,doc_id = 312,content = "今天yoyoyo没来",dtype = "new_knowledge",info = "no split")]
        emb = vectorizor.vectorize(docs, is_query = False)
        print(emb)

if __name__ == "__main__":
    unit_test()
