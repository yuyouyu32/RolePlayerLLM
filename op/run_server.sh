cd ../src/
nohup python3 -m embedding_server.server > ../logs/embedding_server.log 2>&1 &
nohup python3 -m redis_server.server > ../logs/redis_server.log 2>&1 & 
nohup python3 -m model_server.server > ../logs/model_server.log 2>&1 &
nohup python3 -m interface.feishu.server > ../logs/feishu_server.log 2>&1 &