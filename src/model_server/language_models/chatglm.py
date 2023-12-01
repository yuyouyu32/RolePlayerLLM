import torch
import transformers
import sys
from transformers import AutoModel, AutoTokenizer

from model_server.config import *
from .base import BaseLLM
from typing import Tuple

transformers.utils.GENERATION_CONFIG_NAME = None
transformers.utils.cached_file = None
transformers.utils.download_url = None
transformers.utils.extract_commit_hash = None

device = "cuda" if torch.cuda.is_available() else "cpu"

class ChatGLM(BaseLLM):
    def __init__(self, path: str):
        self.model, self.tokenizer = self._get_model(path)
        # default params
        self.max_length = 8192
        self.top_p = 0.8
        self.temperature = 0.95

    def set_params(self, max_length: int =8192, top_p: float =0.8, temperature: float =0.95):
        self.max_length = max_length
        self.top_p = top_p
        self.temperature = temperature

    def _get_model(self, path: str, load_8bit=False):
        """
        Describtion:
            Load the model from the path
        Input:
            path: path to the model
            load_8bit: whether to load the model in 8bit mode
        Output:
            model: the loaded model
            tokenizer: the loaded tokenizer
        """
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
        model = AutoModel.from_pretrained(path, trust_remote_code=True)
        if device == "cuda":
            model = model.cuda()
    
        if not load_8bit:
            model.half()  # seems to fix bugs for some users.
    
        model.eval()
        if torch.__version__ >= "2" and sys.platform != "win32":
            model = torch.compile(model)
        
        return model, tokenizer

    @torch.inference_mode()
    def predict(self, prompt: str, generation_config: dict = None) -> str:
        """
        Describtion:
            Predict the response given the prompt
        Input:
            prompt: the prompt to the model
            generation_config: the generation config to the model
                {
                    "max_length": 8192,
                    "top_p": 0.8,
                    "temperature": 0.95
                }
        Output:
            response: the response from the model
        """
        if generation_config:
            for key, value in generation_config.items():
                setattr(self, key, value)
        response, new_history = self.model.chat(self.tokenizer,
                prompt,
                None,
                max_length=self.max_length,
                top_p=self.top_p,
                temperature=self.temperature)
        return response
    
    @torch.inference_mode()
    def predict_stream(self, prompt: str) -> str:
        """
        Describtion:
            Predict the stream response given the prompt
        Input:
            prompt: the prompt to the model
        Output:
            response: the stream response from the model
        """
        for response, new_history in  self.model.stream_chat(
                        self.tokenizer,
                        prompt,
                        None,
                        max_length=self.max_length,
                        top_p=self.top_p,
                        temperature=self.temperature):
            yield response

def unit_test():
    llm = ChatGLM('/mnt_data/llm_weight/ChatGLM/chatglm2-6b')
    test_rsp = llm.predict("杨戬云川就业怎么样")

if __name__ == "__main__":
    unit_test()

