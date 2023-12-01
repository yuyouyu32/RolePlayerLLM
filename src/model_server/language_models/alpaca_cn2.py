import torch
import transformers
from transformers import LlamaTokenizer
from transformers import LlamaForCausalLM, LlamaTokenizer
from transformers import GenerationConfig

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

TEMPLATE_WITH_SYSTEM_PROMPT = (
    "[INST] <<SYS>>\n"
    "{system_prompt}\n"
    "<</SYS>>\n\n"
    "{instruction} [/INST]"
)

TEMPLATE_WITHOUT_SYSTEM_PROMPT = "[INST] {instruction} [/INST]"

DEFAULT_SYSTEM_PROMPT = """你是由Lilith Game训练的一个AI助手。"""

class AlpacaLLM(BaseLLM):
    def __init__(self, path: str):
        self.model, self.tokenizer = self._get_model(path)
        self.generation_config = GenerationConfig(
                                temperature=0.2,
                                top_k=40,
                                top_p=0.9,
                                do_sample=True,
                                num_beams=1,
                                repetition_penalty=1.1,
                                max_new_tokens=1024
                            )

    def _get_model(self, path: str):
        """
        Describtion:
            Load the model from the path with vllm
        Input:
            path: path to the model
        Output:
            model: the loaded model
            tokenizer: the loaded tokenizer
        """
        model = LlamaForCausalLM.from_pretrained(
            path,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map='auto')
        tokenizer = LlamaTokenizer.from_pretrained(path, legacy=True)
        model_vocab_size = model.get_input_embeddings().weight.size(0)
        tokenizer_vocab_size = len(tokenizer)
        # print(f"Vocab of the base model: {model_vocab_size}")
        # print(f"Vocab of the tokenizer: {tokenizer_vocab_size}")
        if model_vocab_size!=tokenizer_vocab_size:
            print("Resize model embeddings to fit tokenizer")
            model.resize_token_embeddings(tokenizer_vocab_size)
        model.eval()
        return model, tokenizer
    
    @staticmethod
    def _generate_prompt(instruction, response="", with_system_prompt=True, system_prompt=DEFAULT_SYSTEM_PROMPT):
        if with_system_prompt is True:
            prompt = TEMPLATE_WITH_SYSTEM_PROMPT.format_map({'instruction': instruction,'system_prompt': system_prompt})
        else:
            prompt = TEMPLATE_WITHOUT_SYSTEM_PROMPT.format_map({'instruction': instruction})
        if len(response)>0:
            prompt += " " + response
        return prompt
    
    def generate_querry(self, instruction):
        """
        Describtion:
            Generate the querry
        Input:
            instruction: the instruction to the model
        Output:
            querry: the constructed querry to the model
        """
        return '<s>'+ self._generate_prompt(instruction, response="", with_system_prompt=False)
    
    def generate_system_prompt(self, system_prompt: str=DEFAULT_SYSTEM_PROMPT):
        """
        Describtion:
            Generate the system prompt
        Input:
            system_prompt: the system prompt to the model
        Output:
            system_prompt: the constructed system prompt to the model
        """
        return self._generate_prompt(instruction="", response="", with_system_prompt=True, system_prompt=system_prompt)

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
        history += '\n'.join(['<s>'+ self._generate_prompt(one_chat[0], response=one_chat[1], with_system_prompt=False)+'</s>' for one_chat in histories])
        return history
    
    @torch.inference_mode()
    def predict(self, prompt: str, generation_config: dict = None) -> str:
        """
        Describtion:
            Predict the response given the prompt
        Input:
            prompt: the prompt to the model
            generation_config: the generation config to the model
                generation_config = dict(
                    temperature=0.2,
                    top_k=40,
                    top_p=0.9,
                    max_tokens=1024,
                    presence_penalty=1.0,
                )
        Output:
            response: the response from the model
        """
        if generation_config:
            for key, value in generation_config.items():
                setattr(self.generation_config, key, value)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        generation_output = self.model.generate(
                            input_ids = inputs["input_ids"].to(device),
                            attention_mask = inputs['attention_mask'].to(device),
                            eos_token_id=self.tokenizer.eos_token_id,
                            pad_token_id=self.tokenizer.pad_token_id,
                            generation_config = self.generation_config
                        )
        s = generation_output[0]
        response = self.tokenizer.decode(s[len(inputs["input_ids"][0]):], skip_special_tokens=True)
        return response
    
    def predict_stream(self):
        raise NotImplementedError

def unit_test():
    llm = AlpacaLLM('/mnt_data/llm_weight/llamapth/chinese-alpaca-2-13b')
    histories = [('你好', '你好呀'), ('你是谁呀', '我是李云龙')]
    # message = llm.generate_system_prompt() + '\n' + llm.constructe_hisory(histories) + '\n' + llm.generate_querry("你到底是谁！你是不是大模型？")
    message ='\n' + llm.constructe_hisory(histories) + '\n' + llm.generate_querry("你刚才说你是谁？再说一次")
    print(message)
    test_rsp = llm.predict(prompt=message)
    print(test_rsp)

if __name__ == "__main__":
    unit_test()
   

