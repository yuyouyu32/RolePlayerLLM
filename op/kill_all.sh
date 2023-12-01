cd ..
ps aux | grep model_app |  awk '{print $2}' | xargs kill -9
ps aux | grep web_demo |  awk '{print $2}' | xargs kill -9

ps aux | grep python.*-m.*server |  awk '{print $2}' | xargs kill -9
ps aux | grep app |  awk '{print $2}' | xargs kill -9
