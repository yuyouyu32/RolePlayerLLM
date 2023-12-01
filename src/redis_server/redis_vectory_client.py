import redis
from redis.exceptions import ResponseError
from agent.vector_source.document import Document
from typing import List, Dict, Any

import numpy as np
from redis.commands.search.field import (
    NumericField,
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query

from .redis_base import Redis_Base_Client

class RedisVectorClient(Redis_Base_Client):
    def __init__(self, config: Dict[str, Any]):
        """
        Description:
            Initialize the redis vector client.
        Args:
            config:
                The config of redis connection:
                    {
                        'host': 'localhost',
                        'port': 6379, 
                        'db': 0,
                        'password': None,
                        'embedding_config': embedding_config
                    }
                embedding_config is required: 
                    {"m3e_base": 
                        {
                            "path" : "/mnt_data/embedding_weight/chinese/m3e-base", 
                            'threshold': 1000, 
                            'dim': 768, 
                            'ip': '127.0.0.1', 
                            'port': 6550
                        },
                        ...
                    }
        """
        super().__init__(config)
        self.emb_config = config['embedding_config']
    
    def show(self, table_name:str, max_num: int):
        """
        Description:
            Show the table.
        Args:
            table_name: The name of the table.
            max_num: The max number of the results.
        Returns:
            The list of the documents.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            keys = self._scan_keys(f"{table_name}:*")
            docs = []
            for key in keys[:max_num]:
                doc = conn.json().get(key, "$")
                docs.append(doc[0])
        return docs
   
    def create_index(self, table_name: str) -> int:
        """
        Description:
            Create the index of the table.
        Args:
            table_name: The name of the table.
        Returns:
            The number of failures with index.
        """
        # Create Index
        schema = (
            TextField("$.dtime_str", as_name="dtime_str"),
            NumericField("$.sub_doc_id", as_name="sub_doc_id"),
            NumericField("$.doc_id", as_name="doc_id"),
            TextField("$.full_content",  as_name="full_content"),
            TextField("$.dtype", as_name="dtype"),
            TextField("$.info",  as_name="info"),
            TextField("$.content", as_name="content")  
        )

        # Add Vector Fields
        for emb_name, config in self.emb_config.items():
            emb_field = VectorField(
                f"$.emb_{emb_name}",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": config["dim"],
                    "DISTANCE_METRIC": "COSINE",
                },
                as_name=f"emb_{emb_name}",
            )
            schema += (emb_field,)

        definition = IndexDefinition(prefix=[f"{table_name}:"], index_type=IndexType.JSON)

        with redis.Redis(connection_pool=self.connet_pool) as conn:
            conn.ft(f"idx:{table_name}_vss").create_index(fields=schema, definition=definition)
            info = conn.ft(f"idx:{table_name}_vss").info()
        print(f"{info['num_docs']} documents indexed with {info['hash_indexing_failures']} failures by created index.")
        return info['hash_indexing_failures']
    
    def insert(self, table_name: str, docs: List[Document], info=None, dtype=None) -> List[bool]:
        """
        Description:
            Insert the document into the table.
        Args:
            table_name: The name of the table.
            doc: The document to be inserted.
            info: The info of the document. TODO
            dtype: The dtype of the document. TODO 
        Return:
            The list of the failures index with insert.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            pipeline = conn.pipeline()
            for doc in docs:            
                doc_key = f"{table_name}:{doc.sub_doc_id}"
                doc_data = {
                    "sub_doc_id": doc.sub_doc_id,
                    "dtime_str": doc.dtime_str,
                    "doc_id": doc.doc_id,
                    "full_content": doc.full_content,
                    "content": doc.content,
                    "dtype": doc.dtype,
                    "info": doc.info,
                }

                for emb_name, _ in self.emb_config.items():
                    doc_data[f"emb_{emb_name}"] = np.array(doc.embeddings[emb_name]).astype(np.float32).tolist()
                pipeline.json().set(doc_key, "$", doc_data)
            res = pipeline.execute()
            print(f"inserted {len(res)} docs into {table_name}")
            conn.sadd('table_names', table_name)
            try:
                info = conn.ft(f"idx:{table_name}_vss").info()
                print(f"{ info['num_docs']} documents indexed with {info['hash_indexing_failures']} failures")
            except ResponseError:
                self.create_index(table_name)
        return [index for index, value in enumerate(res) if not value]

    def search(self, table_name: str, embedding_name: str, embedding: List[float], topK: int, threshold: float = 0) -> List[Document]:
        """
        Description:
            Search the document by the embedding.
        Args:
            table_name: The name of the table.
            embedding_name: The name of the embedding.
            embedding: The embedding of the query.
            topK: The number of the results.
        Returns:
            The list of the documents.
        """
        index_name = f"idx:{table_name}_vss"
        query_vector = np.array(embedding, dtype=np.float32).tobytes()

        query = (
            Query("(*)=>[KNN {} @emb_{} $query_vector AS vector_score]".format(topK, embedding_name))
            .sort_by("vector_score")
            .return_fields("vector_score", "id", "dtime_str", "sub_doc_id", "doc_id", "full_content", "content", "dtype", "info")
            .dialect(2)
        )
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            results = conn.ft(index_name).search(query, {"query_vector": query_vector}).docs
        docs = []
        for doc in results:
            doc_score = 1- float(doc.vector_score)
            if doc_score < threshold:
                continue
            document = Document(
                content=doc.content,
                dtype=doc.dtype,
                full_content=doc.full_content,
                sub_doc_id=int(doc.sub_doc_id),
                doc_id=int(doc.doc_id),
                info=doc.info,
                score= doc_score,
                dtime_str=doc.dtime_str,
            )
            docs.append(document)

        return docs
    
    def copy_table(self, source_table: str, target_table: str) -> List[bool]:
        """
        Description:
            Copy the table.
        Args:
            source_table: The name of the source table.
            target_table: The name of the target table.
        Return:
            The list of the failures index with copy.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            source_data_keys = self._scan_keys(f"{source_table}:*")
            pipeline = conn.pipeline()
            for key in source_data_keys:
                data = conn.json().get(key, "$")[0]
                for emb_name, _ in self.emb_config.items():
                    data[f"emb_{emb_name}"] = np.array(data[f"emb_{emb_name}"]).astype(np.float32).tolist()
                target_key = key.replace(source_table, target_table)
                pipeline.json().set(target_key, "$", data)
            res = pipeline.execute()
            print(f"copied {len(res)} docs from {source_table} to {target_table}")
            conn.sadd('table_names', target_table)
            try:
                info = conn.ft(f"idx:{target_table}_vss").info()
                print(f"{info['num_docs']} documents indexed with {info['hash_indexing_failures']} failures")
            except ResponseError:
                self.create_index(target_table)
        return [index for index, value in enumerate(res) if not value]