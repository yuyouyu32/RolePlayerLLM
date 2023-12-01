import json
import os
from agent.config import *
from util.session import *
from redis_server.redis_hash_client import RedisHashClient

STATUS_CONFIG_NAME = "status.json"
NUMERIC_KEYS = ["relationship", "happy", "angry", "fear", "fullness", "energy"]
RELATIONSHIP_MAP = {0: "陌生人", 1:"认识但是不熟", 2:"认识但是不熟", 3:"朋友", 4:"朋友",  5:"好朋友", 6:"好朋友", 7:"关系亲密的好朋友"}
HAPPY = {0: "伤痛欲绝", 1: "很伤心", 2:"", 3:"开心",  4:"非常非常开心"}
ANGRY = {0:"平和", 1:"", 2:"", 3:"生气", 4:"暴怒"}
FEAR = {0:"十分安心", 1:"安心", 2:"", 3:"害怕", 4:"极度恐慌"}
HUNGRY = {0:"吃撑了", 1:"吃饱", 2:"", 3:"饥饿", 4:"快饿死了"}
ENERGY = {0:"精疲力尽", 1:"累了", 2:"", 3:"有精神", 4:"元气满满"}

NUMERIC_MAP = {"relationship": RELATIONSHIP_MAP,
               "happy": HAPPY,
               "angry": ANGRY,
               "fear": FEAR}
               #"hungry": HUNGRY,
               #"energy": ENERGY}
STATUS_CHANGE_CONFIG = {"relationship": {"relationship": {"re": [r'态度：(.*?)\(', r'态度：(.*?)（', r'态度：(.*?)\n'], 
                                                          "update_method": "add",
                                                          "postprocess_type": "map",
                                                          "map": {"中性":0, "负面":-1, "正面":1}}},
                        "mood": {"happy": {"re": [r'开心度：(.*?)\(', r'开心度：(.*?)（', r'开心度：(.*?)\n'],
                                           "update_method": "add",
                                           "postprocess_type": "map",
                                           "map": {"普通":0, "悲伤":-1, "开心":1}},
                                 "angry": {"re": [r'愤怒度：(.*?)\(', r'愤怒度：(.*?)（', r'愤怒度：(.*?)\n'],
                                           "update_method": "add",
                                           "postprocess_type": "map",
                                           "map": {"普通":0, "平静":-1, "愤怒":1}},
                                 "fear": {"re": [r'恐惧度：(.*?)\(', r'恐惧度：(.*?)（', r'恐惧度：(.*?)\n'],
                                           "update_method": "add",
                                           "postprocess_type": "map",
                                           "map": {"普通":0, "安心":-1, "恐惧":1}}},
                        "status": {"location": {"re": [r'你在哪：(.*?)\(', r'你在哪里：(.*?)\(', r'你在哪：(.*?)（', r'你在哪里：(.*?)（', r'你在哪：(.*?)\n', r'你在哪里：(.*?)\n'],
                                                "update_method": "update",
                                                "postprocess_type": None},
                                   "action": {"re": [r'你在干什么：(.*?)\(', r'你在干什么：(.*?)（', r'你在干什么：(.*?)\n'],
                                                "update_method": "update",
                                                "postprocess_type": None},
                                   "thought": {"re": [r'你的内心活动：(.*?)\(', r'你的内心活动：(.*?)（', r'你的内心活动：(.*?)\n'],
                                                "update_method": "update",
                                                "postprocess_type": None},
                                   "plan": {"re": [r'你接下来的计划：(.*?)\(', r'你接下来的计划：(.*?)（', r'你接下来的计划：(.*?)\n'],
                                                "update_method": "update",
                                                "postprocess_type": None}}
                        }


PLAN_KEY = "plan"
class AgentStatus():
    # blend to metaHuman
    def __init__(self, config):
        self.redis_client = RedisHashClient(config)
        self.table_name = config["table_name"]
        with open(InitDataConfig, 'r') as f:
            init_config = json.load(f)
        self.content_keys = init_config["status_keys"]
        self.full_keys = ['agent_id'] + init_config["status_keys"]

    def insert_user(self, sess: Session):
        agent_status_config_path = os.path.join(os.path.join(InitDataPath, sess.prototype_id), STATUS_CONFIG_NAME)
        with open(agent_status_config_path, 'r') as f:
            status_dict = json.load(f)

        data_keys = list(status_dict.keys())
        assert len(data_keys) == len(self.content_keys) 
 
        keys = self.full_keys
        values = [sess.agent_id] + list(status_dict.values())

        self.redis_client.insert(self.table_name, keys, values)

    def get(self, sess: Session) -> dict:
        ret = self.redis_client.search(self.table_name, self.content_keys, 'agent_id', sess.agent_id)
        status = {k:v for k,v in zip(self.content_keys, ret)}
        for numeric_key in NUMERIC_MAP.keys():
            status[numeric_key] = int(status[numeric_key])
            status[numeric_key + "_descri"] = NUMERIC_MAP[numeric_key][status[numeric_key]]
        return status 

    def set_status(self, sess: Session, key, value):
        assert key in self.content_keys
        self.redis_client.update(self.table_name, key, value, 'agent_id', sess.agent_id)

    def get_plan_descri(self, sess: Session) -> str:
        assert PLAN_KEY in self.content_keys
        plan = self.redis_client.search(self.table_name, [PLAN_KEY], 'agent_id', sess.agent_id)
        return plan 

    def clear(self, sess: Session):
        self.redis_client.delete(self.table_name, 'agent_id', sess.agent_id)

    def show(self, sess: Session):
        self.redis_client.show(self.table_name)

    def drop_all(self, ):
        self.redis_client.drop_table(self.table_name)

def unit_test():
    sess = Session(user_id = "testid123", prototype_id = "maomao", user_name='jeriflli', agent_id='testid123_maomao')

    status = AgentStatus(StatusDBConfig)
    status.redis_client.flushdb()
    print(status.redis_client.show("status"))
    status.insert_user(sess)
    v = status.get(sess)
    print('v', v)
    status.get_plan_descri(sess)

    v = status.get(sess)
    print(v)

    status.clear(sess)
    status.redis_client.flushdb()

if __name__ == "__main__":
    unit_test()
