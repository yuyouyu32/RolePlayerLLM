import os
import json
from agent.config import *
from util.session import *
from redis_server.redis_hash_client import RedisHashClient

PERSONA_CONFIG_NAME = "persona.json"
class Persona():
    def __init__(self, config):
        self.redis_client = RedisHashClient(config)
        self.table_name = config["table_name"]
        with open(InitDataConfig, 'r') as f:
            init_config = json.load(f)
        self.content_keys = init_config["persona_keys"]
        self.full_keys = ['agent_id'] + init_config["persona_keys"]
        # self.redis_client.create_table(self.table_name, self.full_keys)

    def insert_user(self, sess: Session):
        agent_persona_config_path = os.path.join(os.path.join(InitDataPath, sess.prototype_id), PERSONA_CONFIG_NAME)
        with open(agent_persona_config_path, 'r') as f:
            persona_dict = json.load(f)

        data_keys = list(persona_dict.keys())
        assert len(data_keys) == len(self.content_keys) 
 
        keys = self.full_keys
        values = [sess.agent_id] + list(persona_dict.values())
        self.redis_client.insert(self.table_name, keys, values)

    def get(self, sess: Session) -> dict:
        ret = self.redis_client.search(self.table_name, self.content_keys, 'agent_id', sess.agent_id)
        persona = {k:v for k,v in zip(self.content_keys, ret)}
        return persona 

    def clear(self, sess: Session):
        self.redis_client.delete(self.table_name, 'agent_id', sess.agent_id)

    def show(self, sess: Session):
        self.redis_client.show(self.table_name)

    def drop_all(self, ):
        self.redis_client.drop_table(self.table_name)

def unit_test():
    #person = Persona(PersonaDBConfig)
    #person.drop_all()

    sess = Session(user_id = "testid123", prototype_id = "kuma")

    person = Persona(PersonaDBConfig)


    print(person.redis_client.show("persona"))

    person_dict = person.get(sess)
    print(person_dict)

    person.clear(sess)



if __name__ == "__main__":
    unit_test()

