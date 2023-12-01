import pandas as pd

from sklearn.preprocessing import StandardScaler
from scipy.special import softmax
from typing import List, Dict, Any
from langchain.docstore.document import Document

from agent.config import *
from util.logging import *
from util.session import *
from .config import *
from .vectorization import TrsVectorizor
from redis_server.redis_vectory_client import RedisVectorClient
from .data_loader import *
from .document import Document


class VectorDBBase:
    def __init__(self, config):
        self.btype = "base_"
        self.config = config 
        self.embedding_tools = {}
        self.vectorDB = RedisVectorClient(config)
        for embedding_name, v in embedding_config.items():
            if embedding_name in {"m3e_base", "bge_large_zh"}:
                self.embedding_tools[embedding_name] = TrsVectorizor(v)
            else:
                raise("not support other embedding yet!")    

    def create(self, sess: Session):
        table_name = self.btype + sess.agent_id
        blue_print_copy = self.btype + "blue_print_"+ sess.prototype_id
        if not self.vectorDB.table_exists(blue_print_copy):
            self._create_agent_copy(sess.prototype_id)
        if not self.vectorDB.table_exists(table_name):
            self.vectorDB.copy_table(blue_print_copy, table_name)
            logger.info(f"Table '{table_name}' created by blue print copy.")
        else:
            logger.info(f"Table '{table_name}' already exists.")
    
    def _create_agent_copy(self, prototype_id, reload=False):
        blue_print_copy = self.btype + "blue_print_"+ prototype_id
        if reload or not self.vectorDB.table_exists(blue_print_copy):
            self.vectorDB.drop_table(blue_print_copy)
            docs = load_doc(docloader_configs, prototype_id, self.btype)
            self._add_source(blue_print_copy, docs)
            logger.info(f"Table '{blue_print_copy}' created.")
        else:
            logger.info(f"Table '{blue_print_copy}' already exists and not reload.")


    def clear(self, sess: Session):
        table_name = self.btype + sess.agent_id
        self.vectorDB.drop_table(table_name)

    def _normalize_and_softmax(self, input_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Describtion:
            Normalize the score and apply softmax
        Input:
            input_dict: results from retriever
        Output:
            normalized_and_softmax_results: normalized and softmaxed results
        """
        results_df = pd.DataFrame.from_dict(input_dict, orient='index', columns=['content', 'score'])

        scaler = StandardScaler()
        results_df[['score']] = scaler.fit_transform(results_df[['score']])

        results_df['score'] = softmax(results_df['score'].to_numpy())
        normalized_and_softmax_results = results_df.to_dict(orient='index')

        return normalized_and_softmax_results
    
    def _merge_and_rank(self, input_data: Dict[str, List[Document]]) -> List[str]:
        """
        Describtion:
            Merge the results from different retrievers
        Input:
            input_data: results from different retrievers
        Output:
            sorted_page_contents: sorted page contents
        """
        # 1. merge docs
        merged_docs = {}
        for embedding_name, docs in input_data.items():
            if len(docs) == 0:
                continue

            # handle doc without doc_id, TODO: optimize
            max_doc_id = max([doc.doc_id for doc in docs])
            for idx in range(len(docs)):
                if docs[idx].doc_id == -1:
                    max_doc_id += 1
                    docs[idx].doc_id = max_doc_id

            input_dict = {doc.doc_id:{"content": doc.full_content, "score": doc.score} for doc in docs}
            normalized_and_softmax_results = self._normalize_and_softmax(input_dict)
            for docid, data in normalized_and_softmax_results.items():
                if docid not in merged_docs:
                    merged_docs[docid] = {"content": data["content"], "scores": {}, "merge_score": 0.0}
                merged_docs[docid]["scores"][embedding_name] = data["score"]

        # 2. merge scores
        for docid, doc in merged_docs.items():
            for embedding_name, score in doc["scores"].items():
                merged_docs[docid]["merge_score"] += retrievers_merge_weight[embedding_name] * score

        sorted_docs = sorted(merged_docs.items(), key=lambda x: x[1]["merge_score"], reverse=True)
        for _, doc in sorted_docs:
            logger.debug(f"-------------------------\n{doc['content']}\n{doc['scores']}\n{doc['merge_score']}")

        sorted_page_contents = [entry[1]["content"] for entry in sorted_docs]
        return sorted_page_contents
    
    def get_source(self, sess: Session, search_query_info: dict, keep_max_k: int = 10, querry_max_k: int = 20) -> str:
        """
        Describtion:
            Get the source documents from the knowledge base
        Input:
            querry_input: query info dict
            keep_max_k: number of documents to keep
            querry_max_k: number of documents to query
        Output:
            source: source documents
        """
        table_name = self.btype + sess.agent_id
        # 1. search DB
        original_docs = {}
        for emb_name, embedding_tool in self.embedding_tools.items():
            emb = embedding_tool.vectorize(search_query_info, is_query=True)
            docs = self.vectorDB.search(table_name, emb_name, emb, querry_max_k, self.config[emb_name]['threshold'])
            original_docs[emb_name] = docs
        # 2. merge and rerank
        texts = self._merge_and_rank(original_docs)  

        # 3. to string
        formatted_strings = []
        for idx, text in enumerate(texts):
            if idx >= keep_max_k:
                break
            formatted_strings.append("{}. {}".format(idx+1, text))
        source = "\n".join(formatted_strings)
        # logger.info(f"\n=======source========\n{source}\n")
        return source
    
    def add_source(self, sess: Session, new_docs: List[Document]):
        table_name = self.btype + sess.agent_id
        self._add_source(table_name, new_docs)

    def _add_source(self, table_name: str, new_docs: List[Document]):
        batches = [new_docs[i:i + embedding_cal_batch_size] for i in range(0, len(new_docs), embedding_cal_batch_size)]

        for batch in batches:
            for emb_name, embedding_tool in self.embedding_tools.items():
                batch_embeddings = embedding_tool.vectorize(batch, is_query=False)
                for i, emb in enumerate(batch_embeddings):
                    batch[i].embeddings[emb_name] = emb     

            failures = self.vectorDB.insert(table_name, batch)
            logger.debug(f"\ninserted {len(batch)} docs into {table_name}, {len(failures)} failures {failures}\n")

    def show(self, sess: Session, max_num: int):
        table_name = self.btype + sess.agent_id
        result = self.vectorDB.show(table_name, max_num)
        return result
            

def unit_test():
    from agent.vector_source.config import embedding_config
    sess = Session()
    from agent.query_analysis import QueryAnalysis 
    qa = QueryAnalysis()
    db_config = {
    'host': 'localhost',
    'port': 6379, 
    'db': 0,
    'password': None,
    'embedding_config': embedding_config
    }
    
    kb = VectorDBBase(db_config)
    kb.vectorDB.flushdb()
    kb.btype = "knowledge_"
    kb.create(sess)
    docs = [Document(content='你好啊', dtype='test', full_content='你好啊', sub_doc_id=1, doc_id=1, info='test', dtime=None, dtime_str=None),
            Document(content='今天天气怎么样', dtype='test', full_content='今天天气怎么样', sub_doc_id=2, doc_id=2, info='test', dtime=None, dtime_str=None),
            Document(content='最近过得好吗', dtype='test', full_content='最近过得好吗', sub_doc_id=3, doc_id=3, info='test', dtime=None, dtime_str=None),
            Document(content='喜欢旅游吗', dtype='test', full_content='喜欢旅游吗', sub_doc_id=4, doc_id=4, info='test', dtime=None, dtime_str=None),
            Document(content='你有宠物吗', dtype='test', full_content='你有宠物吗', sub_doc_id=5, doc_id=5, info='test', dtime=None, dtime_str=None),
            Document(content='最喜欢的音乐是什么', dtype='test', full_content='最喜欢的音乐是什么', sub_doc_id=6, doc_id=6, info='test', dtime=None, dtime_str=None),
            Document(content='最近看过什么电影', dtype='test', full_content='最近看过什么电影', sub_doc_id=7, doc_id=7, info='test', dtime=None, dtime_str=None),
            Document(content='喜欢运动吗', dtype='test', full_content='喜欢运动吗', sub_doc_id=8, doc_id=8, info='test', dtime=None, dtime_str=None),
            Document(content='你的梦想是什么', dtype='test', full_content='你的梦想是什么', sub_doc_id=9, doc_id=9, info='test', dtime=None, dtime_str=None),
            Document(content='最喜欢的食物是什么', dtype='test', full_content='最喜欢的食物是什么', sub_doc_id=10, doc_id=10, info='test', dtime=None, dtime_str=None)]
    kb.add_source(sess, docs)

    querry_input = "hahaha是谁？"
    search_query_info = qa.process(querry_input)
    source = kb.get_source(sess, search_query_info, keep_max_k = 5, querry_max_k=20)
    print(source)
    
    querry_input = "yoyoyo是谁？"
    search_query_info = qa.process(querry_input)
    source = kb.get_source(sess, search_query_info, keep_max_k = 5, querry_max_k=20)
    print(source)
    kb.clear(sess)
    kb.vectorDB.flushdb()

if __name__ == "__main__":
    unit_test()
