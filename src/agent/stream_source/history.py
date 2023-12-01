import datetime
from util.logging import *
from util.session import *
from typing import Tuple, List, Dict, Any
from agent.stream_source.event import Event
from redis_server.redis_time_client import RedisTimeClient

class History:
    def __init__(self, config: Dict[str, Any]):
        """
        Description:
            init history for each chatbot
        Input:
            idx: str, for chatbot to identify which user's history to use
        """
        self.step = 0
        self.table_name = "history"
        self.redis_time = RedisTimeClient(config)   

    def get(self, session: Session, event_types: list, postprocess: str = None, keep_num: int = 2):
        """
        Description:
            get all history of this chatid, not set limit numbers yet.
        Input:
            keep_num: int, the number of history to keep
        Output:
            history: str, the history of this chatid
        """
        assert type(event_types) == list 
        if keep_num == -1:
            keep_num = self.step
        # history, event terms:  List[Dict]
        history = self.redis_time.search(table_name=f"{self.table_name}_{session.agent_id}", event_types=event_types, keep_num=keep_num)
        history.reverse()
        if postprocess == None:
            return history
        elif postprocess == "chat_pair":
            assert len(event_types)==1 and event_types[0]=="chat"
            history_pairs = [(event.obs, event.rsp) for event in history]
            return history_pairs
        #else:
        #    history_descri = ""
        #    for event in history:
        #        if event_type == "chat":
        #            prompt_content = {"obs": event['obs'],"rsp":event['rsp']}
        #            event_descri = build_prompt_with_template(HistoryChatPromptTemplate, prompt_content)
        #        elif event_type == "reflection":
        #            prompt_content = {"reflection": event['ref']}
        #            event_descri = build_prompt_with_template(HistoryReflectPromptTemplate, prompt_content)
        #        elif event_type == "act":
        #            prompt_content = {"obs": event['obs'],"rsp":event['rsp']}
        #            event_descri = build_prompt_with_template(HistoryActPromptTemplate, prompt_content)
        #        history_descri += "\n" + event_descri
        #    return (history_descri, history[-1]["time"])
    
    def add(self, session: Session, event: Event):
        """
        Description:
            update history with new chat
        """
        logger.debug("add history!")
        self.redis_time.insert_data(table_name=f"{self.table_name}_{session.agent_id}", event=event)

    def clear(self, session: Session):
        """
        Description:
            clear all history of this chatid
        """
        self.redis_time.drop_table(table_name=f"{self.table_name}_{session.agent_id}")

from agent.config import *
def unit_test():
    db_config = {
    'host': 'localhost',
    'port': 6379, 
    'db': 0,
    'password': None,
    } 
    session = Session()
    history = History(db_config)
    history.clear(session)
    print("add_history: ")
    event = Event(obs = '你谁啊', \
                  rsp = '我是猪啊', \
                  ref = '他是傻子？', \
                  dtime = datetime.datetime.now(),
                  event_type = "chat")
    history.add(session, event)
    event = Event(obs = '啊！', \
                  rsp = 'pxh是🐖吗？', \
                  ref = '他确实是！', \
                  dtime = datetime.datetime.now(),
                  event_type = "chat")
    history.add(session, event)
    event = Event(obs = 'good！', \
                  rsp = 'pxh是傻子！', \
                  ref = '他肯定是！', \
                  dtime = datetime.datetime.now(),
                  event_type = "chat")
    history.add(session, event)
    print('get_history: {}'.format(history.get(session, ["chat",], postprocess='chat_pair')))
    history.clear(session)


if __name__ == "__main__":
    unit_test()

