from agent.config import *
from util.session import *
from redis_server.redis_hash_client import RedisHashClient


class User():
    def __init__(self, config):
        self.redis_client = RedisHashClient(config)
        self.table_name = config["table_name"]
        self.full_keys = ['agent_id', 'user_id', 'prototype_id', 'user_name', 'table_creation_status']
        self.content_keys = self.full_keys[1:]

    def insert_user(self, sess: Session):
        keys = self.full_keys
        values = [sess.agent_id, sess.user_id, sess.prototype_id, sess.user_name, "False"]
        assert len(keys) == len(values)
        self.redis_client.insert(self.table_name, keys, values, primary_key='agent_id')
    
    def get_status(self, sess: Session):
        ret = self.redis_client.search(self.table_name, ['table_creation_status'], 'agent_id', sess.agent_id)
        return True if ret[0] == 'True' else False

    def set_status(self, sess: Session):
        self.redis_client.update(self.table_name, 'table_creation_status', 'True', 'agent_id', sess.agent_id)
        
    def get(self, sess: Session) -> dict:
        ret = self.redis_client.search(self.table_name, self.content_keys, 'agent_id', sess.agent_id)
        persona = {k:v for k,v in zip(self.content_keys, ret)}
        return persona 

    def del_user(self, sess: Session):
        self.redis_client.delete(self.table_name, 'agent_id', sess.agent_id)

    def show(self):
        self.redis_client.show(self.table_name)

    def drop_all(self):
        self.redis_client.drop_table(self.table_name)
    
    def id_exists(self, sess: Session):
        return self.redis_client.value_exists(self.table_name, 'agent_id', sess.agent_id)

    def clear(self, sess: Session):
        self.redis_client.delete(self.table_name, 'agent_id', sess.agent_id)
    
    def __del__(self):
        del self.redis_client

def unit_test():

    sess = Session(user_id = "test_id123", prototype_id = "kuma", user_name='jeriflli', agent_id='test_id123_kuma')

    user = User(UserInfoDBconfig)
    user.redis_client.flushdb()
    print(user.id_exists(sess))
    user.insert_user(sess)
    print(user.id_exists(sess))
    
    user.show()

    user_dict = user.get(sess)
    print(user_dict)

    user.set_status(sess)

    user_dict = user.get(sess)
    print(user_dict)
    user.del_user(sess)



if __name__ == "__main__":
    unit_test()

