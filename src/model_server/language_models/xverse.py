import torch
import transformers
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.utils import GenerationConfig

from model_server.config import *
from .base import BaseLLM
from typing import Tuple, List, Dict

transformers.utils.GENERATION_CONFIG_NAME = None
transformers.utils.cached_file = None
transformers.utils.download_url = None
transformers.utils.extract_commit_hash = None

device = "cuda" if torch.cuda.is_available() else "cpu"

DEFAULT_SYSTEM_PROMPT = """你是由Lilith Game训练的一个AI语音助手"""

class XverseLLM(BaseLLM):
    def __init__(self, path: str):
        # default params
        self.model, self.tokenizer = self._get_model(path)

    def _get_model(self, path: str, load_8bit: bool=False):
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
        model = AutoModelForCausalLM.from_pretrained(path, device_map="auto", torch_dtype=torch.bfloat16, trust_remote_code=True)
        model.generation_config = GenerationConfig.from_pretrained(path)

        if device == "cuda":
            model = model.cuda()
    
        if not load_8bit:
            model.half()  # seems to fix bugs for some users.
    
        model.eval()
        if torch.__version__ >= "2" and sys.platform != "win32":
            model = torch.compile(model)
        
        return model, tokenizer
    
    @staticmethod
    def _generate_message(role, content):
        return {"role": role, "content": content}
    
    def generate_querry(self, instruction):
        """
        Describtion:
            Generate the querry
        Input:
            instruction: the instruction to the model
        Output:
            querry: the constructed querry to the model
        """
        return self._generate_message("user", instruction)
    
    def generate_system_prompt(self, system_prompt: str=DEFAULT_SYSTEM_PROMPT):
        """
        Describtion:
            Generate the system prompt
        Input:
            system_prompt: the system prompt to the model
        Output:
            system_prompt: the constructed system prompt to the model
        """
        raise NotImplementedError("Xverse model does not support system prompt")

    def constructe_hisory(self, histories: List[Tuple[str, str]] = None) -> List[Dict[str, str]]:
        """
        Describtion:
            Construct the history from the histories
        Input:
            histories: the histories to construct
        Output:
            history: the history prompt constructed from the histories
        """
        history = []
        if histories:
            for dialog in histories:
                history.extend([self._generate_message("user", dialog[0]), self._generate_message("assistant", dialog[1])])
        return history
    
    def constructe_messages(self, instruction: str, system_prompt:str = DEFAULT_SYSTEM_PROMPT, histories: List[Tuple[str, str]] = None) -> List[Dict]:
        """
        Describtion:
            Construct the messages from the instruction, system_prompt and histories
        Input:
            instruction: the instruction to the model
            system_prompt: the system prompt to the model
            histories: the histories to construct
        Output:
            messages: the messages constructed from the instruction, system_prompt and histories
        """
        messages = []
        
        messages.extend(self.constructe_hisory(histories))
        if system_prompt:
            messages.append((self.generate_querry(f'{system_prompt}\n{instruction}')))
        else:
            messages.append(self.generate_querry(instruction))
        return messages


    @torch.inference_mode()
    def predict(self, prompt: List[Dict], generation_config: Dict = None) -> str:
        """
        Describtion:
            Predict the response given the prompt
        Input:
            prompt: the prompt to the model
            generation_config: the generation config to the model
               {
                    "pad_token_id": 1,
                    "bos_token_id": 2,
                    "eos_token_id": 3,
                    "max_new_tokens": 2048,
                    "temperature": 0.5,
                    "top_k": 30,
                    "top_p": 0.85,
                    "repetition_penalty": 1.1,
                    "do_sample": true,
                    "transformers_version": "4.29.1"
                }
        Output:
            response: the response from the model
        """
        if generation_config:
            for key, value in generation_config.items():
                setattr(self.model.generation_config, key, value)
        response = self.model.chat(self.tokenizer, prompt)
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

        for response in self.model.chat(
                        self.tokenizer,
                        prompt,
                        stream=True):
            yield response

def unit_test():
    llm = XverseLLM('/mnt_data/llm_weight/XVERSE-13B-Chat')
    histories = [('你好， 中国首都是哪里', '中国的首都是北京。'), ('这个地方有什么特色吗？', '北京是一个拥有丰富历史文化遗产和现代化城市风貌的城市。它是中国的政治、经济、文化中心之一,同时也是世界著名的旅游目的地。这里有许多著名的景点,如故宫、天安门广场、长城等。此外,北京的美食也非常有特色,如北京烤鸭、炸酱面等。')]

    messages = llm.constructe_messages('他还有什么特色美食？', histories=histories, system_prompt=None)
    print(messages)
    test_rsp = llm.predict(messages, generation_config={"max_new_tokens": 1024})
    print(test_rsp)

if __name__ == "__main__":
    unit_test()

