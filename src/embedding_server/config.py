embedding_config = \
{
    #"tfidf": {"path" : "/mnt_data/embedding_weight/chinese/tfidf", 'threshold': {"full":0.56, "kw":0.34}},
    #"bm25": {"path" : "/mnt_data/embedding_weight/chinese/bm25", 'threshold': {"full":25, "kw":8.5}},
    "m3e_base": {"path" : "/mnt_data/embedding_weight/chinese/m3e-base", 'threshold': 0.7, 'dim': 768, 'ip': '127.0.0.1', 'port': 6550},
    "bge_large_zh": {"path": "/mnt_data/embedding_weight/chinese/bge-large-zh", 'threshold': 0.7, 'dim': 1024, 'ip': '127.0.0.1', 'port': 6551}
}
