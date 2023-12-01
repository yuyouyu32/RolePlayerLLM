from .config import *
from .database_controller import *
from agent.vector_source.knowledge import Knowledge
from agent.vector_source.memory import Memory
import os
from agent.config import InitDataPath
from agent.config import RedisDBConfig

ReloadAgent = ['maomao']

def create_vector_copy(db_config):
    if db_config['table_name'] == 'knowledge':
        vector_db = Knowledge(db_config)
    else:
        vector_db = Memory(db_config)
    # vector_db.vectorDB.flushdb()
    prototype_ids = [entry.name for entry in os.scandir(InitDataPath) if entry.is_dir()]
    for prototype_id in prototype_ids:
        if prototype_id in ReloadAgent:
            vector_db._create_agent_copy(prototype_id, reload=True)
        else:
            vector_db._create_agent_copy(prototype_id)

if __name__ == "__main__":
    start_redis(RedisConfigPath)
    for db_name in {'knowledge', 'memory'}:
        create_vector_copy(RedisDBConfig[db_name])