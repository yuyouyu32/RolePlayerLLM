import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from transformers import GenerationConfig


from .base import BaseLLM
from .qwen_generation_utils import make_context, decode_tokens
from typing import Tuple, List, Dict


class QwenLLM(BaseLLM):
    def __init__(self, path: str, batch_infer = False):
        # default params
        self.batch_infer = batch_infer
        self.model, self.tokenizer = self._get_model(path)

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
        if not self.batch_infer:
            tokenizer = AutoTokenizer.from_pretrained(path, use_fast=False, trust_remote_code=True)
            # use bf16
            # model = AutoModelForCausalLM.from_pretrained(path, device_map="auto", trust_remote_code=True, bf16=True).eval()
            # use fp16
            # model = AutoModelForCausalLM.from_pretrained(path, device_map="auto", trust_remote_code=True, fp16=True).eval()
            # use cpu only
            # model = AutoModelForCausalLM.from_pretrained(path, device_map="cpu", trust_remote_code=True).eval()
            # use auto mode, automatically select precision based on the device.
            model = AutoModelForCausalLM.from_pretrained(path, device_map="auto", trust_remote_code=True, use_flash_attn=True).eval()
        else:
            tokenizer = AutoTokenizer.from_pretrained(
                path,
                pad_token='<|extra_0|>',
                eos_token='<|endoftext|>',
                padding_side='left',
                trust_remote_code=True
                )
            model = AutoModelForCausalLM.from_pretrained(
                    path,
                    pad_token_id=tokenizer.pad_token_id,
                    device_map="auto",
                    trust_remote_code=True
                ).eval()
            model.generation_config = GenerationConfig.from_pretrained(path, pad_token_id=tokenizer.pad_token_id)
        return model, tokenizer
    
    @torch.inference_mode()
    def predict(self, prompt: str, system_prompt: str, history: List[Tuple[str, str]], generation_config: dict = None) -> str:
        """
        Describtion:
            Predict the response given the prompt
        Input:
            prompt: the prompt to the model,
            history: the history to the model,
            generation_config: the generation config to the model
                {
                    "chat_format": "chatml",
                    "eos_token_id": 151643,
                    "pad_token_id": 151643,
                    "max_window_size": 6144,
                    "max_new_tokens": 512,
                    "do_sample": true,
                    "top_k": 0,
                    "top_p": 0.8,
                    "repetition_penalty": 1.1,
                    "transformers_version": "4.31.0"
                }
        Output:
            response: the response from the model
        """
        if generation_config:
            generation_config = GenerationConfig(**generation_config)
        response, _ = self.model.chat(tokenizer = self.tokenizer, query = prompt, history = history, system = system_prompt, generation_config = generation_config)
        return response
    
    @torch.inference_mode()
    def predict_stream(self, prompt: str, system_prompt: str, history: List[Tuple[str, str]], generation_config: dict = None) -> str:
        """
        Describtion:
            Predict the stream response given the prompt
        Input:
            prompt: the prompt to the model,
            history: the history to the model,
            generation_config: the generation config to the model
                {
                    "chat_format": "chatml",
                    "eos_token_id": 151643,
                    "pad_token_id": 151643,
                    "max_window_size": 6144,
                    "max_new_tokens": 512,
                    "do_sample": true,
                    "top_k": 0,
                    "top_p": 0.8,
                    "repetition_penalty": 1.1,
                    "transformers_version": "4.31.0"
                }
        Output:
            response: the stream response from the model
        """
        if generation_config:
            generation_config = GenerationConfig(**generation_config)
        for response in self.model.chat_stream(tokenizer = self.tokenizer, query = prompt, history = history, system = system_prompt, generation_config = generation_config):
            yield response

    @torch.inference_mode()
    def predict_batch(self, prompts: List[str], system_prompts: List[str], histories: List[List[Tuple[str, str]]], generation_config: dict = None) -> str:
        if generation_config:
            generation_config = GenerationConfig(**generation_config)
            generation_config.pad_token_id=self.tokenizer.pad_token_id
        batch_raw_text = []
        for q, s, h in zip(prompts, system_prompts, histories):
            raw_text, _ = make_context(
                self.tokenizer,
                q,
                system= s,
                history= h,
                max_window_size=self.model.generation_config.max_window_size,
                chat_format=self.model.generation_config.chat_format,
            )
            batch_raw_text.append(raw_text)

        batch_input_ids = self.tokenizer(batch_raw_text, padding='longest')
        batch_input_ids = torch.LongTensor(batch_input_ids['input_ids']).to(self.model.device)
        batch_out_ids = self.model.generate(
            batch_input_ids,
            return_dict_in_generate=False,
            generation_config=self.model.generation_config
        )
        padding_lens = [batch_input_ids[i].eq(self.tokenizer.pad_token_id).sum().item() for i in range(batch_input_ids.size(0))]

        batch_response = [
            decode_tokens(
                batch_out_ids[i][padding_lens[i]:],
                self.tokenizer,
                raw_text_len=len(batch_raw_text[i]),
                context_length=(batch_input_ids[i].size(0)-padding_lens[i]),
                chat_format="chatml",
                verbose=False,
                errors='replace'
            ) for i in range(len(prompts))
        ]
        return batch_response
def unit_test():
    import time
    from test_data import sys_p, query, history
    now = time.time()
    # llm = QwenLLM('/mnt_data/llm_weight/Qwen-14B-Chat', batch_infer=True)
    llm = QwenLLM('/mnt_data/llm_weight/Qwen-14B-Chat', batch_infer=False)
    end = time.time()
    print("load time cost: {}".format(end - now))
    now = time.time()
    # rsp_batch = llm.predict_batch(prompts=query, system_prompts=sys_p, histories=history)
    for sys_p, query, history in zip(sys_p, query, history):
        rsp_batch = llm.predict(prompt=query, system_prompt=sys_p, history=history)
        # print(rsp_batch)
    end = time.time()
    print("predit time cost: {}".format(end - now))
    print(rsp_batch)
    

if __name__ == "__main__":
    unit_test()