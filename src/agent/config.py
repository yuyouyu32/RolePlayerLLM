from agent.vector_source.config import embedding_config

stopword_paths = ["../data/qa/stopwords/baidu_stopwords.txt",
                 "../data/qa/stopwords/scu_stopwords.txt",
                 "../data/qa/stopwords/hit_stopwords.txt",
                 "../data/qa/stopwords/cn_stopwords.txt"]
synonym_path = "../data/qa/synonyms.txt"

# agent init 
InitDataPath = "../agent_init_data/"
InitDataConfig = "../agent_init_data/config.json"

# DB info
PersonaDBConfig = {
                    'host': 'localhost',
                    'port': 6379, 
                    'db': 1,
                    'password': None,
                    "table_name": 'persona'
                }
StatusDBConfig = {
                    'host': 'localhost',
                    'port': 6379, 
                    'db': 1,
                    'password': None,
                    "table_name": 'status'
                }
MemoryDBConfig = {
                    'host': 'localhost',
                    'port': 6379, 
                    'db': 0,
                    'password': None,
                    "table_name": 'memory',
                    "embedding_config": embedding_config
                }
KnowledgeDBConfig = {
                    'host': 'localhost',
                    'port': 6379, 
                    'db': 0,
                    'password': None,
                    "table_name": 'knowledge',
                    "embedding_config": embedding_config
                }

UserInfoDBconfig = {
                    'host': 'localhost',
                    'port': 6379, 
                    'db': 2,
                    'password': None,
                    "table_name": 'user_info'
                }
HistoryDBConfig = {
                    'host': 'localhost',
                    'port': 6379, 
                    'db': 3,
                    'password': None,
                    "table_name": 'history'
                }


RedisDBConfig = {'persona': PersonaDBConfig, 'status': StatusDBConfig, 'memory': MemoryDBConfig, 'knowledge': KnowledgeDBConfig, 'user_info': UserInfoDBconfig, 'history': HistoryDBConfig}
