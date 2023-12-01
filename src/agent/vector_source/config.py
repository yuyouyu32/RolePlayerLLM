from embedding_server.config import embedding_config

docloader_configs = {"separator":"@@@",
                       "chunk_size": 1,
                       "chunk_overlap": 0}

retrievers_merge_weight = {"tfidf": 0.2, "bm25":0.3, "bge_large_zh":0.5, "m3e_base": 0.3}

embedding_cal_batch_size = 512
