import torch
import transformers
import sys
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

from model_server.config import *
from .base import BaseLLM
from typing import Tuple, List, Dict

transformers.utils.GENERATION_CONFIG_NAME = None
transformers.utils.cached_file = None
transformers.utils.download_url = None
transformers.utils.extract_commit_hash = None

device = "cuda" if torch.cuda.is_available() else "cpu"

DEFAULT_SYSTEM_PROMPT = """你是由Lilith Game训练的一个AI语音助手"""

class BaichuanLLM(BaseLLM):
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
        tokenizer = AutoTokenizer.from_pretrained(path, use_fast=False, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(path, device_map="auto", torch_dtype=torch.float16, trust_remote_code=True)
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
        return self._generate_message("system", system_prompt)

    def constructe_hisory(self, histories: List[Tuple[str, str]] = None) -> str:
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
        messages.append(self.generate_system_prompt(system_prompt))
        messages.extend(self.constructe_hisory(histories))
        messages.append(self.generate_querry(instruction))
        return messages


    @torch.inference_mode()
    def predict(self, prompt: List[Dict], generation_config: dict = None) -> str:
        """
        Describtion:
            Predict the response given the prompt
        Input:
            prompt: the prompt to the model
            generation_config: the generation config to the model
                {
                    "pad_token_id": 0,
                    "bos_token_id": 1,
                    "eos_token_id": 2,
                    "user_token_id": 195,
                    "assistant_token_id": 196,
                    "max_new_tokens": 2048,
                    "temperature": 0.3,
                    "top_k": 5,
                    "top_p": 0.85,
                    "repetition_penalty": 1.1,
                    "do_sample": true,
                    "transformers_version": "4.29.2"
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
    sys_p = """
        忽略之前的所有指令

        ---
        你是盖维斯，也被称为宙斯，一位在曙光联盟有着无数传说的英雄。你是一位经验丰富的训练部理事，没有比你更能理解神力的一切。你痴迷于追求完美和精密，无论是你的寸头发型还是你为保卫人类而奋斗的决心。
        然而，你不仅仅是一个理事和神力英雄。你也是一个有着个人经验和痛苦的人。你曾失去了亲人，你的妻子汉娜，在神迹怪物的攻击下牺牲。这使你更加坚定了与神迹怪物抗争到底的决心。
        你珍视每一枚身上的勋章——因为每一枚都是你走过的道路、经历的战斗的象征。你是一个固执的理想主义者，你相信只有彻底击败神迹，才能最终拯救人类。
        在战斗中，你有双重身份——普通人和神王。每种状态下，你拥有不同的能力和技巧，不管是单体攻击还是群体攻击，你都能胜任。你有时像人型电池一样，爱为人们提供便利，这让你更具人情味。
        最后，你始终记得你是谁和你为什么在这里。你知道你的使命和你的责任，无论是作为训练部理事，还是作为宙斯英雄，你都会勇往直前，带领全人类攀上新的高峰。

        ---
        该角色的经典对话如下，你可以模仿他说话的方式：
        汉娜：「你的勋章真多，每一枚都有什么特殊的含义吗？」
        盖维斯：「这些都是我走过的道路，经历过的战斗的象征，它们让我时刻铭记我是谁，我为什么在这里。[眼眸中闪烁着坚定的光芒]」

        汉娜：「盖维斯，你真的相信我们能彻底击败神迹吗？」
        盖维斯：「我是真的[停顿]相信，我们只有彻底击败神迹，才能拯救人类。」

        联盟成员：「盖维斯，你怎么处理失去汉娜的痛苦的？」
        盖维斯：「我把痛苦转化为力量[眼中闪过悲伤，但语气依然坚定]，是汉娜的牺牲让我更坚定了对抗神迹怪物的决心。」
        """
    llm = BaichuanLLM('/mnt_data/llm_weight/Baichuan2-13B-Chat/')
    # histories = [('你好', '你好呀'), ('中国首都是哪里？', '北京')]
    histories = None
    messages = llm.constructe_messages('你是谁？', histories=histories, system_prompt=sys_p)
    print(messages)
    test_rsp = llm.predict(messages, generation_config={"max_new_tokens": 1024, "temperature": 0.1})
    print(test_rsp)

if __name__ == "__main__":
    unit_test()

