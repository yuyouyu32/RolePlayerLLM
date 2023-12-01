import jieba
import jieba.analyse
import spacy
from agent.config import *

class QueryAnalysis():
    def __init__(self,):
        # load spacy
        #self.nlp = spacy.load("zh_core_web_sm")
        # load stopword
        self.stop_words = set([]) 
        for stopword_path in stopword_paths:
            with open(stopword_path, "r") as f: 
                for t in f.readlines():
                    self.stop_words.add(t.strip())
        # load synonym
        self.synonym_dict = {}
        with open(synonym_path, "r") as f: 
            for line in f.readlines():
                words = line.strip().split("\t")
                for w in words:
                    self.synonym_dict[w] = [ws for ws in words if ws != w]

    def process_jieba(self, text: str) -> dict:
        query_info = {}
        query_info["content"] = text
        query_info["tokens"] = [t for t in jieba.cut(text, cut_all=True)]
        query_info["keywords"] = [t for t in jieba.analyse.extract_tags(text, topK=5, withWeight=True)]
        return query_info
    
    def process_spacy(self, text: str) -> dict:
        doc = self.nlp(text)

        query_info = {}
        query_info["content"] = text
        query_info["tokens"] = [token.text for token in doc]
        query_info["keywords"] = [token.text for token in doc if token.text not in self.stop_words]
        query_info["postags"] = [(token.text, token.pos_) for token in doc]
        return query_info

    def add_synonyms(self, query_info: dict):
        for token in query_info["tokens"]:
            if token in self.synonym_dict:
                query_info["synonyms"].extend(self.synonym_dict[token])

    def process(self, text: str) -> dict:
        query_info = self.process_jieba(text)
        #query_info = self.process_spacy(text)
        #self.add_synonyms(query_info) 
        return self.process_jieba(text)
    

def unit_test():
    qa = QueryAnalysis()
    text = "雅典娜要几命"
    #text = "哪个英雄的技能会禁疗？"
    #text = "雅典娜的技能有曼沙珠华效果？"
    query_info = qa.process(text)
    print(query_info)

if __name__ == "__main__":
    unit_test()
