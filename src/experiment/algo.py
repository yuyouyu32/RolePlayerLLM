from sglmagent.src.agent.algo_source.algo import AlgoBase
from typing import Tuple

class CustomAlgo(AlgoBase):
    """
    Define sepicific algorithm pipeline, including prompt build function and choose models
    """
    def __init__(self,):
        """
        Define requirement of each prompt builder
        """
        self.chat_history_num = 2   # length of chat_histories in model.predict({"system_prompt": system_prompt, "instruction": instruction, "histories": chat_histories})
        self.prompt_requirement = {"chat": {"query":{},    # observation["query"]
                                            "persona":{},    # kuma/persona.json
                                            "knowledge":{"keep_num":2},    # kuma/knowledge_
                                            "memory":{},    # kuma/memory_, and memory add by remember
                                            "plan":{},    # kuma/status.json, and will changed by agent.plan()
                                            "status":{}}}    # kuma/status.json

    def _build_chat_prompt(self, prompt_content: str) -> Tuple[str, str]:
        """
        Description:
            build prompt for LLM chat
        Input:
            prompt_content: Dict of required data
        Ouput:
            system prompt, instruction
        """
        system_prompt = """
忽略之前的所有指令
---
你需要扮演一个{}, {}
---
你常说的话：{}
""".format(prompt_content["persona"]["persona"],prompt_content["persona"]["background"],  prompt_content["persona"]["talk_examples"])
    
        chat_prompt = """
"""

        if "knowledge" in prompt_content:
            knowledge_part = """
你知道：
{}
""".format(prompt_content["knowledge"])
            chat_prompt += knowledge_part
       
        if "memory" in prompt_content:
            memory_part = """
你记得：
{}
--
""".format(prompt_content["memory"])
            chat_prompt += memory_part

        tail_part = """ 
根据以上信息，请回答问题:「{}」
千万不要说你自己是大模型！你现在是{},你说话{},请尽量模仿以下语言风格回答,例子:{}
--
答：
""".format(prompt_content["query"], prompt_content["persona"]["persona"], prompt_content["persona"]["style"], prompt_content["persona"]["talk_examples"])
        chat_prompt += tail_part 
        return system_prompt, chat_prompt
