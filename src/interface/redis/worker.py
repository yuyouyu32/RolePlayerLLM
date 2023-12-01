from util.session import Session
from agent.agent import Agent
from .config import bot_config
import re
import argparse
from interface.redis.task_queue import get_chat_task, finish_chat_task, publish_chat_ret_task
import asyncio
from datetime import datetime, timedelta

def cut_sent(para: str):
    para = para.strip('\'"')
    para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    para = para.rstrip()
    return para.split("\n")

async def worker(bot: Agent):
    """
    pull chat task from redis queue(worker_chat_task_id, worker_chat_data)
    worker_chat_data:
    {
        "session": {
            "user_id": "ou_3542842ffa3d2f034da611e3e0045c44",
            "user_name": "志凯",
            "prototype_id": "kuma",
            "pair_id": "ou_3542842ffa3d2f034da611e3e0045c44_kuma",
            "agent_id": "ou_3542842ffa3d2f034da611e3e0045c44_kuma"
            
            },
        "observation": {
            "query": "你喜欢我吗",
            "time": "2023-09-27 08:25:19.015570",
            "interact": "你被志凯打了一下",
            },
        "action_type": "chat",
    }
    """
    while True:
        worker_chat_task_id, worker_chat_data = get_chat_task()
        if worker_chat_task_id is None:
            await asyncio.sleep(1)
            continue
        print("worker_chat_task_id: ", worker_chat_task_id)
        print("worker_chat_data: \n", worker_chat_data)
        # message = json.loads(worker_chat_data)
        session_config = worker_chat_data['session']
        session = Session(**session_config)
        worker_chat_ret_data = {
            "agent_id": session.agent_id,
            "pair_id": session.pair_id,
            "content": "",
            "status": ""
        }
        if worker_chat_data['action_type'] not in bot.methods:
            worker_chat_ret_data["info"] = {"status_code": 405, "descripition": "Action type not supported!"}
            return
        # Init
        bot.set_bot(bot_config, session)
        bot.session_init()
        # Rsponse
        observation = worker_chat_data['observation']
        time = observation["time"]
        rsp = bot.methods[worker_chat_data['action_type']](observation)
        content, worker_chat_ret_data["status"] = rsp["content"], rsp['status']
        worker_chat_ret_data["info"] = {"status_code": 200, "descripition": "success"}
        print("worker_chat_ret_data: \n", worker_chat_ret_data)
        # Cut sentence
        for sentence in cut_sent(content):
            if sentence == "":
                continue
            worker_chat_ret_data["content"] = sentence
            # Publish chat ret task
            publish_chat_ret_task(worker_chat_ret_data, time + len(sentence) * 0.2)
        finish_chat_task(worker_chat_task_id)
        # Sleep
        await asyncio.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--bot_count", type=int, default=1, help="Number of bots to launch")
    args = parser.parse_args()
    bots = [Agent() for _ in range(args.bot_count)]
    tasks = [asyncio.ensure_future(worker(bot)) for bot in bots]
    asyncio.get_event_loop().run_until_complete(asyncio.gather(*tasks))