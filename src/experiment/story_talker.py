import datetime
from util.session import Session
from agent.agent import Agent
from typing import Tuple, List, Any

story_chapters = [
"""
从前，在莉莉丝游戏公司，有一位传奇程序员kuma。他总是喜欢说：“就是，是吧”，“是吧”，“对吧”，“啊对对对”。他热衷于打dota游戏和做饭，每天兴致勃勃地投入工作。

一天，老板ben想出了一个大胆的游戏创意，他决定让kuma带领浩男、志凯、博士、strong、gogo、hahaha和yoyoyo一起开发这个新游戏。这款游戏的主角是一只狗狗，它必须带领一群猫和狗的英雄团队打败邪恶的反派，拯救世界。

""",
"""
kuma充满激情地担任团队领导，为了让游戏更具趣味性，他特地邀请了浩男的狗狗“兜兜”担任游戏形象代言。由于志凯人才出众，kuma总是称赞他是个好人，但有时也会戏谑地说：“志凯人是一个好人，但是吧。”故事情节中，博士家的猫“酋长”成为兜兜的得力助手，这让大家想起了已经离职的博士，回忆起她的美好时光。

在开发过程中，团队遇到了各种有趣的挑战。strong的编程能力得到了广泛认可，他的技巧使得游戏场景变得非常逼真。gogo则将其美术天赋运用到游戏中，让画面充满独特的魅力。hahaha负责游戏的运营和推广，他的幽默感让整个团队在紧张的开发过程中时常发出欢笑。而yoyoyo则以泳哥的身份在游戏中出现，给玩家提供丰富的指导。

每当团队解决了一个难题，kuma总是会高兴地说：“啊对对对！我们终于解决了这个问题，对吧？”这让整个团队充满了干劲。为了缓解工作压力，kuma会邀请大家一起打dota游戏，分享彼此的喜好和技巧，有时甚至会赛跑，看谁先从公司冲到附近的水果摊，以此消遣。
""",
"""
经过几个月的努力，kuma和他的团队终于成功完成了这款游戏。游戏上线后，迅速成为了市场上的热门作品，玩家们对于兜兜与酋长的冒险故事爱不释手。莉莉丝游戏公司因此声名大噪，而kuma也被推上了职业生涯的新高峰。

这个传奇故事在游戏行业广为传颂，kuma和他的团队也因此成为了业界的佼佼者。如今，他们继续在莉莉丝游戏公司辛勤工作，用智慧和幽默为玩家们带来更多精彩的游戏。而这段奇幻冒险，成为了他们心中永恒的瑰宝。
"""]

def story_agent_test():
    session = Session()
    test_config = {"use_knowledge": True,
                   "use_memory": False,
                   "use_chat_history": True}
    bot = Agent(config = test_config)
    bot.set_session(session)
    bot.session_init()

    observation = {"query": "你是谁", "source": "志凯", "time": datetime.datetime.now()}
    test_rsp = bot.chat(observation)

    new_knowledges = [story_chapters[0]]
    bot.add_knowledge(new_knowledges)

    observation = {"query": "ben提出了什么创意？", "source": "志凯", "time": datetime.datetime.now()}
    test_rsp = bot.chat(observation)

    new_knowledges = [story_chapters[1]]
    bot.add_knowledge(new_knowledges)

    observation = {"query": "hahaha在团队里负责什么？", "source": "志凯", "time": datetime.datetime.now()}
    test_rsp = bot.chat(observation)

    new_knowledges = [story_chapters[2]]
    bot.add_knowledge(new_knowledges)

    observation = {"query": "你们的游戏成功了吗", "source": "志凯", "time": datetime.datetime.now()}
    test_rsp = bot.chat(observation)

    bot.clear()


if __name__ == "__main__":
    story_agent_test()
