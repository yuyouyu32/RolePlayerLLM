from task_queue import publish_chat_task, get_chat_task, finish_chat_task
from task_queue import publish_chat_ret_task, get_chat_ret_task, finish_chat_ret_task
from task_queue import publish_chat_act_task, get_chat_act_task, finish_chat_act_task
from task_queue import publish_chat_act_ret_task, get_chat_act_ret_task, finish_chat_act_ret_task


### app ben ###

print("\n app \n")

# 发布 chat 任务
app_pub_data = {
    "session": {
        "user_id": "u123",
        "user_name": "Ben",
        "prototype_id": "maomao",
        "pair_id": "pr456",
        "agent_id": "u123_maomao"
    },
    "observation": {
        "query": "",
        "time": "2021-09-01 10:30:00",
        "interact": "text"
    },
    "action_type": "chat"
}
for query in ["你是谁啊？", "你好啊", "你喜欢ben吗？"]:
    app_pub_data["observation"]["query"] = query
    publish_chat_task(app_pub_data)

### app ben ###


#################################################################################################
#################################################################################################
#################################################################################################


# ### llm worker yyy ###

# # 获取 chat 任务
# worker_chat_task_id, worker_chat_data = get_chat_task()
# print(worker_chat_task_id, worker_chat_data)


# # 处理
# worker_pair_id = worker_chat_data["session"]["pair_id"]
# worker_content = worker_chat_data["observation"]["query"]
# worker_processed_content = worker_content + "111"
# finish_chat_task(worker_chat_task_id)
# # 发布 chat ret 任务
# worker_chat_ret_data = {"pair_id": worker_pair_id, "content": worker_processed_content}
# publish_chat_ret_task(worker_chat_ret_data)

# # 发布 chat act 任务
# worker_chat_act_data = {"pair_id": worker_pair_id, "action": "take picture"}
# publish_chat_act_task(worker_chat_act_data)

### llm worker yyy ###


# #################################################################################################
# #################################################################################################
# #################################################################################################
