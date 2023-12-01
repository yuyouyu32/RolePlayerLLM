import os
from typing import List,Tuple,Dict,Any
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.document_loaders import DirectoryLoader, TextLoader
from agent.config import InitDataPath
from .document import Document

def process_doc(docs: List[Document], use_sub_split: bool = True) -> List[Document]:
    """
    Describtion:
        Split the document into smaller pieces
    Input:
        docs: original doc
        use_sub_split: whether to split the document into smaller pieces
    Output:
        doc_map: map doc_id to original doc
        sub_docs: smaller doc pieces with sub_docs.metadata["doc_id"]
    """
    MaxSubNum = 1000
    processed_docs = []

    enhance_text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n","\n","。"],chunk_size=500,
                                                chunk_overlap=50,
                                                keep_separator=False)
    for idx, doc in enumerate(docs):
        if len(doc.page_content)>=50 and use_sub_split:
            cur_sub_docs = enhance_text_splitter.split_documents([doc])
            for sub_idx, sub_doc in enumerate(cur_sub_docs):
                processed_doc = Document(sub_doc_id = idx*MaxSubNum + cur_sub_docs,
                                   doc_id = idx,
                                   full_content = doc.page_content,
                                   content = sub_doc.page_content,
                                   dtype = "init_knowledge",
                                   info = 'split')
                processed_docs.append(processed_doc)
        else:
            processed_doc = Document(sub_doc_id = idx,
                               doc_id = idx,
                               content = doc.page_content,
                               dtype = "init_knowledge",
                               info = 'no split')
            processed_docs.append(processed_doc)
    return processed_docs 

def load_doc(config: dict, agent_id: str, btype: str) -> List[Document]:
    """
    Describtion:
        Load text from docloader_configs
    Input:
        docloader_configs: configs for loading text
    Output:
        all_docs: list of documents
    """
    # TODO: not use lanchain document
    data_path = os.path.join(os.path.join(InitDataPath, agent_id), btype)
    if os.path.isdir(data_path):
        loader = DirectoryLoader(data_path, loader_cls=TextLoader)
    else:
        raise ValueError(f'{data_path} is not a dir')

    documents = loader.load()
    if "separator" in config and config["separator"]: 
        text_splitter = CharacterTextSplitter(separator=config["separator"], chunk_size=config["chunk_size"], chunk_overlap=config["chunk_overlap"])
    else:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=config["chunk_size"], chunk_overlap=config["chunk_overlap"])
    org_docs = text_splitter.split_documents(documents)
  
    processed_docs = process_doc(org_docs, use_sub_split=False)
    return processed_docs 
