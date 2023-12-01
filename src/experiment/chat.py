import datetime
from util.session import Session
from agent.agent import Agent
from typing import Tuple, List, Any

def chat_agent_test():
    session = Session()
    test_config = {"use_knowledge": True,
                   "use_memory": False,
                   "use_chat_history": True}
    bot = Agent(config = test_config)
    bot.set_session(session)
    #bot.session_init()
    observation = {"query": "你是谁", "source": "志凯", "time": datetime.datetime.now()}
    test_rsp = bot.chat(observation)
    observation = {"query": "你喜欢我吗", "source": "志凯", "time": datetime.datetime.now()}
    test_rsp = bot.chat(observation)
    observation = {"query": "你认识hahaha吗", "source": "志凯", "time": datetime.datetime.now()}
    test_rsp = bot.chat(observation)
    observation = {"query": "博士去哪里了", "source": "志凯", "time": datetime.datetime.now()}
    test_rsp = bot.chat(observation)
    #bot.clear()


if __name__ == "__main__":
    chat_agent_test()
