from agent.agent import Agent
from util.session import Session


def unit_test():
    import datetime
    session = Session()
    test_config = {"use_knowledge": True,
                   "use_memory": False,
                   "use_chat_history": True}
    bot = Agent(config = test_config)
    bot.set_session(session)
    bot.session_init()
    while 1:
        q_o = input("请输入问题: ")
        observation = {"query": q_o, "source": "志凯", "time": datetime.datetime.now()}
        test_rsp = bot.chat(observation)
    print("final rsp:")
    print(test_rsp)

    bot.clear()

if __name__ == "__main__":
    unit_test()

