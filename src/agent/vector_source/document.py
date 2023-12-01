import datetime

class Document:
    dtime_format = "%Y-%m-%d %H:%M:%S"
    def __init__(self, content: str,
                       dtype: str,
                       embeddings: dict = None,
                       full_content: str = None,
                       sub_doc_id: int = -1,
                       doc_id: int = -1,
                       info: str = None,
                       score: float = 0.0,
                       dtime: datetime.datetime = None,
                       dtime_str: str = None):
        if embeddings is None:
            self.embeddings = {}
        else:  
            self.embeddings = embeddings
        self.content = content
        self.dtype = dtype
        self.sub_doc_id = sub_doc_id
        self.doc_id = doc_id
        self.info = info
        self.score = score
        self.dtime = dtime
        self.dtime_str = dtime_str
        self.full_content = full_content
        if self.full_content == None: self.full_content = self.content
        if self.dtime == "None": self.dtime = None
        if self.dtime_str == "None": self.dtime_str = None
        if self.dtime or self.dtime_str:
            if not self.dtime:
                self.dtime = datetime.datetime.fromisoformat(dtime_str)
            if not self.dtime_str:
                self.dtime_str = self.dtime.isoformat() 


