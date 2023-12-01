import requests
import json
import base64
import time
import urllib.parse
from datetime import datetime

headers = {"X-token": "01HB8BT26EGFKFPZD5MA3N7TH5"}
q_url_base = "https://aihub-dev.supergameai.com/api/ai-hub-dev/"


CHAT_QUEUE          = "queue_test_chat"
CHAT_RET_QUEUE      = "queue_test_chat_ret_"
CHAT_ACT_QUEUE      = "queue_test_chat_act"
CHAT_ACT_RET_QUEUE  = "queue_test_chat_ret_"


def publish_task(queue_name, delay, ttl, tries, data):

    q_url = q_url_base + "%s?delay=%d&ttl=%d&tries=%d"%(queue_name, delay, ttl, tries)
    json_data = json.dumps(data)
    ret = requests.put(q_url, headers = headers, data = json_data)

    print("pub", ret.text)


def get_task(queue_name, timeout = 1):

    q_url = q_url_base + "%s?timeout=%d"%(queue_name, timeout)

    try:
        ret = requests.get(q_url, headers = headers)
        content = json.loads(ret.text)

        if content["msg"] == "new job":

            data_b64 = content["data"]
            data = base64.b64decode(data_b64).decode('utf-8')
            data = urllib.parse.unquote_plus(data)
            data_dict = json.loads(data)

            print("get", content["job_id"])

            return content["job_id"], data_dict
        else:
            return None, None

    except:
        print("get task error")

        return None


def finish_task(queue_name, task_id):

    q_url = q_url_base + "%s/job/%s"%(queue_name, task_id)

    for i in range(5):
        try:
            ret = requests.delete(q_url, headers = headers)
            if ret.status_code == 204:
                break
        except:
            print("finish_tts_task error, retry")
            time.sleep(1)


# 从app发到机器人的聊天请求
def publish_chat_task(data):
    publish_task(queue_name = CHAT_QUEUE, delay = 0, ttl = 60, tries = 3, data = data)


# 机器人获取聊天请求
def get_chat_task():
    return get_task(queue_name = CHAT_QUEUE)


# 机器人获取聊天请求完成
def finish_chat_task(task_id):
    finish_task(queue_name = CHAT_QUEUE, task_id = task_id)


# 从机器人发到app的聊天请求回复
def publish_chat_ret_task(data, publish_time = None):
    pair_id = data["pair_id"]
    if publish_time is None:
        publish_task(queue_name = CHAT_RET_QUEUE + pair_id, publish_time = datetime.now().timestamp(), ttl = 60, tries = 3, data = data)
    else:
        publish_task(queue_name = CHAT_RET_QUEUE + pair_id, publish_time = publish_time, ttl = 60, tries = 3, data = data)


# 格式 "2021-01-01 00:00:00"
def publish_chat_ret_task_with_delay(data, send_time):
    pair_id = data["pair_id"]

    time_now = datetime.now()
    send_time = datetime.strptime(send_time, "%Y-%m-%d %H:%M:%S")

    time_delta = int((send_time - time_now).total_seconds())

    if time_delta < 0:
        time_delta = 0

    publish_task(queue_name = CHAT_RET_QUEUE + pair_id, delay = time_delta, ttl = 60, tries = 3, data = data)


# app获取聊天请求回复
def get_chat_ret_task(pair_id):
    return get_task(queue_name = CHAT_RET_QUEUE + pair_id)

# app获取聊天请求回复完成
def finish_chat_ret_task(pair_id, task_id):
    finish_task(queue_name = CHAT_RET_QUEUE + pair_id, task_id = task_id)


# 从机器人发到ue的动作请求
def publish_chat_act_task(data):
    publish_task(queue_name = CHAT_ACT_QUEUE, delay = 0, ttl = 60, tries = 3, data = data)


# ue 获取动作请求
def get_chat_act_task():
    return get_task(queue_name = CHAT_ACT_QUEUE)


# ue 获取动作请求完成
def finish_chat_act_task(task_id):
    finish_task(queue_name = CHAT_ACT_QUEUE, task_id = task_id)


# 从ue发到app的动作
def publish_chat_act_ret_task(data):
    pair_id = data["pair_id"]
    publish_task(queue_name = CHAT_ACT_RET_QUEUE + pair_id, delay = 0, ttl = 60, tries = 3, data = data)


# app获取动作
def get_chat_act_ret_task(pair_id):
    return get_task(queue_name = CHAT_ACT_RET_QUEUE + pair_id)


# app获取动作完成
def finish_chat_act_ret_task(pair_id, task_id):
    finish_task(queue_name = CHAT_ACT_RET_QUEUE + pair_id, task_id = task_id)








def query_q_size():


    q_url = "https://ttsapi.supergameai.com/api/obtts/tts-queue/size"

    for i in range(5):
        try:
            ret = requests.get(q_url, headers = headers)
            if ret.status_code == 200:
                content = json.loads(ret.text)
                return content["size"]

        except:
            print("query_q_size error, retry")
            time.sleep(1)