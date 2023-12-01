MODEL_CLASS = {
        'baichuan-13b': ('model_server.language_models.baichuan', 'BaichuanLLM', '/mnt_data/llm_weight/Baichuan-13B-Chat'),
        'chatglm2-6b': ('model_server.language_models.chatglm', 'ChatGLM', '/mnt_data/llm_weight/ChatGLM/chatglm2-6b'),
        'firefly-baichuan-13b': ('model_server.language_models.baichuan', 'BaichuanLLM', '/mnt_data/llm_weight/firefly-baichuan-13b'),
        'alpaca-cn2-13b': ('model_server.language_models.alpaca_cn2', 'AlpacaLLM', '/mnt_data/llm_weight/llamapth/chinese-alpaca-2-13b'),
        'llama-cn2-13b': ('model_server.language_models.llama_cn2', 'Llama2CNLLM', '/mnt_data/llm_weight/llamapth/Llama2-Chinese-13b-Chat'),
        'xverse-13b':('model_server.language_models.xverse', 'XverseLLM', '/mnt_data/llm_weight/XVERSE-13B-Chat'),
        'baichuan-13b-2':('model_server.language_models.baichuan', 'BaichuanLLM', '/mnt_data/llm_weight/Baichuan2-13B-Chat'),
        'Qwen-14B-Chat': ('model_server.language_models.qwen', 'QwenLLM', '/mnt_data/llm_weight/Qwen-14B-Chat'),
    }

MODEL_NAME = "Qwen-14B-Chat"
MODEL_SERVER_IP = "127.0.0.1" 
MODEL_SERVER_PORT = 8725 
