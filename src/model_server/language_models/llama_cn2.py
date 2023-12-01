import torch
import transformers
from transformers import AutoTokenizer, AutoModelForCausalLM
from .base import BaseLLM
from typing import Tuple, List

transformers.utils.GENERATION_CONFIG_NAME = None
transformers.utils.cached_file = None
transformers.utils.download_url = None
transformers.utils.extract_commit_hash = None

if torch.cuda.is_available():
    device = torch.device(0)
else:
    device = torch.device('cpu')

DEFAULT_SYSTEM_PROMPT = """你是由Lilith Game训练的一个AI助手"""

class Llama2CNLLM(BaseLLM):
    def __init__(self, path: str):
        # default params
        self.model, self.tokenizer = self._get_model(path)
        self.generate_input = {
            "input_ids": "",
            "max_new_tokens":512,
            "do_sample":True,
            "top_k":50,
            "top_p":0.95,
            "temperature":0.3,
            "repetition_penalty":1.3,
            "eos_token_id": self.tokenizer.eos_token_id,
            "bos_token_id": self.tokenizer.bos_token_id,
            "pad_token_id": self.tokenizer.pad_token_id
        }
    def _get_model(self, path: str):
        """
        Describtion:
            Load the model from the path
        Input:
            path: path to the model
        Output:
            model: the loaded model
            tokenizer: the loaded tokenizer
        """
        model = AutoModelForCausalLM.from_pretrained(path,device_map='auto',torch_dtype=torch.float16,load_in_8bit=True)
        model =model.eval()
        tokenizer = AutoTokenizer.from_pretrained(path,use_fast=False)
        tokenizer.pad_token = tokenizer.eos_token
        return model, tokenizer
    
    @staticmethod
    def generate_querry(instruction):
        """
        Describtion:
            Generate the querry
        Input:
            instruction: the instruction to the model
        Output:
            querry: the constructed querry to the model
        """
        return "<s>Human: {instruction}\n</s><s>Assistant: ".format(instruction=instruction)
    
    @staticmethod
    def generate_system_prompt(system_prompt: str=DEFAULT_SYSTEM_PROMPT):
        """
        Describtion:
            Generate the system prompt
        Input:
            system_prompt: the system prompt to the model
        Output:
            system_prompt: the constructed system prompt to the model
        """
        return "<s>System: {system_prompt}\n</s>".format(system_prompt=system_prompt)

    def constructe_hisory(self, histories: List[Tuple[str, str]]) -> str:
        """
        Describtion:
            Construct the history from the histories
        Input:
            histories: the histories to construct
        Output:
            history: the history prompt constructed from the histories
        """
        history = ""
        history += '\n'.join([("<s>Human: "+ one_chat[0].replace('<br>','\n')+'\n</s>' if one_chat[0] else '')  +"<s>Assistant: "+ one_chat[1].replace('<br>','\n')+'\n</s>' for one_chat in histories])
        return history

    @torch.inference_mode()
    def predict(self, prompt: str, generation_config: dict = None) -> str:
        """
        Describtion:
            Predict the response given the prompt
        Input:
            prompt: the prompt to the model
            generation_config: the generation config to the model
                generation_config = {
                            "input_ids": "",
                            "max_new_tokens":512,
                            "do_sample":True,
                            "top_k":50,
                            "top_p":0.95,
                            "temperature":0.3,
                            "repetition_penalty":1.3,
                            "eos_token_id": self.tokenizer.eos_token_id,
                            "bos_token_id": self.tokenizer.bos_token_id,
                            "pad_token_id": self.tokenizer.pad_token_id
                            }
        Output:
            response: the response from the model
        """
        if generation_config:
            for key, value in generation_config.items():
                setattr(self.generate_input, key, value)
        input_ids = self.tokenizer([prompt], return_tensors="pt",add_special_tokens=False).input_ids.to(device)
        self.generate_input["input_ids"] = input_ids
        generate_ids = self.model.generate(**self.generate_input)[0]
        response = self.tokenizer.decode(generate_ids[len(input_ids[0]):],skip_special_tokens=True)
        return response
    
    def predict_stream(self):
        raise NotImplementedError("Not implemented yet")


def unit_test():
    llm = Llama2CNLLM('/mnt_data/llm_weight/llamapth/Llama2-Chinese-13b-Chat')
    histories = [('你好', '你好呀'), ('你是谁呀', '我是你的助手')]
    message = llm.generate_system_prompt() + '\n' + llm.constructe_hisory(histories) + '\n' + llm.generate_querry("你是谁训练的？")
    test_rsp = llm.predict(prompt=message)
    print(test_rsp)

if __name__ == "__main__":
    unit_test()
   