import os
import shutil
import json
import pickle
import websockets
import asyncio
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from collections import defaultdict

from sklearn.preprocessing import StandardScaler
from scipy.special import softmax
from typing import List, Dict, Any, Tuple
from langchain.docstore.document import Document

from util.logging import *
from .config import *
from .base import *
from .document import Document

class Knowledge(VectorDBBase):
    def __init__(self, config):
        super().__init__(config)
        self.btype = f"{config['table_name']}_"

def unit_test():
    sess = Session()
    from agent.query_analysis import QueryAnalysis 

    kb = VectorDBBase(KnowledgeDBConfig)
    kb.create(sess)
    qa = QueryAnalysis()

    querry_input = "hahaha来没来"
    search_query_info = qa.process(querry_input)
    source = kb.get_source(sess, search_query_info, keep_max_k = 5, querry_max_k=20)
    print(source)

    new_doc = {"sub_doc_id": 123,
               "doc_id": 312,
               "content": "今天yoyoyo没来",
               "dtype": "new_knowledge",
               "info": "no split"}
    new_docs = [new_doc]
    table_name = kb.btype + sess.agent_id
    kb.add_source(table_name, new_docs)

    querry_input = "yoyoyo来没来"
    search_query_info = qa.process(querry_input)
    source = kb.get_source(sess, search_query_info, keep_max_k = 5, querry_max_k=20)
    print(source)

if __name__ == "__main__":
    unit_test()
