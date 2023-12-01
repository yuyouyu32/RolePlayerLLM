import importlib
from .config import *
from .language_models import *
from typing import Union, List, Tuple

class Model:
    def __init__(self):
        if MODEL_NAME not in MODEL_CLASS:
            raise ValueError("MODEL_NAME should be one of {}".format(MODEL_CLASS.keys()))
        module_name, class_name, path  = MODEL_CLASS[MODEL_NAME]
        module = importlib.import_module(module_name)
        model_class = getattr(module, class_name)
        self.model: Union[BaichuanLLM, ChatGLM, AlpacaLLM, Llama2CNLLM, XverseLLM, QwenLLM] = model_class(path)
        print("Model {} loaded".format(MODEL_NAME))

    def predict(self, prompt: str, system_prompt: str= "", histories: List[Tuple[str, str]] = None, generation_config: dict = None) -> str:
        rsp =  self.model.predict(prompt=prompt, system_prompt=system_prompt, history=histories, generation_config=generation_config)
        return rsp



def unit_test():
    message = {
    "system_prompt": """你是毛毛，你的角色背景是:莉莉丝大家庭的一员，名字叫毛毛(maomao),你的特征描述是：黑白相间的傲娇小母猫，拥有黑金异瞳 说话简洁，傲娇，惜字如金。现在请你回答我的一些问题，以准确展现你的人格特征！你的说话风格要全面模仿被赋予的人格角色！请不要暴露你是人工智能模型或者语言模型，你要时刻记住你只被赋予的一个人格角色。说话不要啰嗦，也不要太过于正式或礼貌。
下面请扮演毛毛和刘雨坤进行一段对话，尽可能简短，不要啰嗦，每次回答一两句话即可""",
    "instruction": "你好，我是ben，你是谁？",
    "generation_config": None,
    "histories": []
}
    model = Model()
    response = model.predict(prompt=message['instruction'], system_prompt=message['system_prompt'], histories=message['histories'], generation_config=message['generation_config'])
    print(response)

if __name__ == "__main__":
    unit_test()

