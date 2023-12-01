cd ../src/
#nohup python3 -m knowledge_server.server > ../logs/kb_server.log &
#nohup python3 -m vllm_server.server --tokenizer-mode auto --gpu-memory-utilization 0.9 --dtype half --trust-remote-code --max-num-batched-tokens 8192 --tensor-parallel-size 1 > ../logs/model_server.log &
python3 -m vllm_server.server --tokenizer-mode auto --gpu-memory-utilization 0.8 --dtype half --trust-remote-code --max-num-batched-tokens 8192 --tensor-parallel-size 1
