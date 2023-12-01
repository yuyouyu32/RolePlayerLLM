"""Example Python client for vllm.entrypoints.api_server"""

import argparse
import json
from typing import Iterable, List
import requests
from .config import *
message = """你的名字是Dislyte AI Sprite，你是由Lilith Game训练的,已知信息：
1. &VIP经验:
2. 体力补给包:	补充60点体力，协助迅速开始新的行动。
3. &乌鸦信函:	&占坑
4. $ 34.99 抵用券:	可以抵用一次$ 34.99 额度的付费
5. 体力上限加成:	30天内，体力上限增加60。
6. $ 24.99 抵用券:	可以抵用一次$ 24.99 额度的付费
7. 品质为故事的联盟悬赏-与自己的对话：
观看一段真熙的故事，如果你也喜欢做手账，欢迎和真熙交流心得。
完成奖励为 钻石: 50。
8. $ 49.99 抵用券:	可以抵用一次$ 49.99 额度的付费
9. $ 19.99 抵用券:	可以抵用一次$ 19.99 额度的付费
10. $ 29.99 抵用券:	可以抵用一次$ 29.99 额度的付费
11. $ 0.99 抵用券:	可以抵用一次 $ 0.99 额度的付费
12. 品质为故事的联盟悬赏-补偿：
观看一段唐轩的故事，照顾别人的前提是照顾好自己。
完成奖励为 钻石: 50。 

根据上述已知信息，简洁和专业地来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是：体力上限是什么"""

message = """
你的名字是Dislyte AI Sprite，你是由Lilith Game训练的,已知信息：
1. 尤弥尔-恩布拉的队长技能是：在积分赛、曙光大师赛中，我方全体暴击率增加30%
尤弥尔-恩布拉的英雄技能包括：
尤弥尔-恩布拉的的技能1 凋敝之剑：攻击 1 个敌方，伤害为自身攻击力 <A102>100%</> 。目标没有<A105>【腐败之种】</>时，为其附加 1 层<A105>【腐败之种】</>；目标有<A105>【腐败之种】</>时，使用<A102>凋敝之剑</>追击其他 1 个随机敌方，每回合触发 1 次。
等级2，伤害提升至105%
等级3，伤害提升至110%
等级4，伤害提升至115%
等级5，伤害提升至120%
【腐败之种】：携带者受击时，获得 1 层【腐败之种】，有 50% 概率获得 2 回合【禁疗】，为攻击者净化 1 个减益。被引爆时对携带者造成伤害，附加 2 回合【流血】，每层伤害为此状态施加者 35% 攻击力（自动引爆时按照满层造成伤害）；该状态提前结束时视为被引爆，满层或携带者死亡时为自动引爆。自动引爆时将该状态传染给携带者 2 个友方，清除携带者此状态。最多可叠加 8 层。该状态消失时，施加者获得 30% 行动值提升。施加者死亡时清除该状态。
【禁疗】：无法受到治疗。
【流血】：回合开始时受到伤害，伤害为状态附加者攻击力 50% 。
2. 神石寄宿者-神石寄宿者是一名初始星级为2的英雄。它的初始速度为90。
它的英雄技能包括：
技能1 破裂一击：对敌方1个目标造成攻击力 <A102>120%</> 的伤害，有 <A102>30%</> 概率附加 1 回合<A105>【流血】</>状态。
【流血】：回合开始时受到伤害，伤害为状态附加者攻击力 50% 。
技能2 爆裂一击：对敌方全体造成攻击力 <A102>100%</> 的伤害，自身拥有增益效果时，则对敌方全体造成攻击力 <A102>200%</> 的伤害。
技能1 弱化之咒：对敌方1个目标造成攻击力 <A102>120%</> 的伤害，延长目标所有减益状态 1 回合。
技能2 凛冬之咒：对敌方全体造成攻击力 <A102>100%</> 的伤害，有 <A102>30%</> 的概率附加 1 回合<A105>【冰冻】</>状态。
【冰冻】：无法进行任何行动。
技能1 制裁之咒：对敌方1个目标造成攻击力 <A102>120%</> 的伤害，有 <A102>30%</> 概率附加 1 回合<A105>【禁疗】</>状态。
【禁疗】：无法受到治疗。
技能2 终结冲击：对敌方全体造成攻击力 <A102>100%</> 的伤害，并为我方全体附加 2 回合<A104>【暴击提升】</>状态。
【暴击提升】：暴击提升 30% 。
3. 亚罕莫德的第4段履历为：时常可以发现亚罕莫德在下城区的街道上散步，购买街头小吃。虽然过去的生活无法被弥补，但亚罕莫德并没有成为一个心胸狭隘的人，而是从这份不幸中走出了自己的道路。亚罕莫德是一位大明星，但是他从未忘记自己来自什么地方。他希望以自己的努力，避免更多的孩子陷入和他曾经的境地。无论工作多么繁忙，他一定会抽出时间来做慈善工作，尤其是需要照顾孩子的工作。在帮助与自己有着同样艰辛童年的孩子们时，他找到了内心的救赎。他对这片土地有很深的感情，也想要尽自己的力量，守护这里的人们。 亚罕莫德的英雄能力是：亚罕莫德是一名拥有高频治疗和提升攻击能力的辅助型代行者。生之序曲能攻击敌人三次且每次可以对我方一个目标进行治疗。世界舞台使亚罕莫德可以连续对我方目标治疗十次，并且降低我方代行者的技能冷却时间。暖心之音是亚罕莫德的核心能力，他每次治疗的目标都是我方生命值比例最低的单位，并且会在治疗前恢复其生命值上限，同时为其治疗目标叠加 1 层【应援之歌】，提升友方的攻击能力；若目标生命值比例低于 50% ，还会额外为其叠加 1 层【应援之歌】。觉醒之后，亚罕默德在治疗前还会净化掉其【禁疗】效果。亚罕莫德的英雄描述是：如大地般沉稳的他将使用盖布的力量治愈人心。亚罕莫德所在的英雄小组名称是：绝妙的演出。亚罕莫德所在的英雄小组成员是：布琳,卢卡斯,亚罕莫德。亚罕莫德的英雄小组故事是：义演举办在即，布琳、亚罕莫德和卢卡斯正在练习室内加紧排练。他们想为观众呈现一场完美的演出，这可不是件容易的事。三人各自的节目都已准备到位，舞台合作却状况频出。问题常常出在精神小伙卢卡斯身上，一旦进入亢奋状态，他会不自觉地开始即兴创作。这让两位队友难以配合，尤其是布琳。她本就因为要登上大舞台而有些紧张，卢卡斯的脱轨令她更加无措。亚罕莫德适时对两人伸出援手，经验丰富的大明星成为了乐队的主心骨。但对于不擅长与人交流的他，协调整个团队可是个不小的挑战。不少朋友在旁观了三人的排练后，替他们捏把汗。布琳笑着让大家放心：虽然生活喜欢出难题，但音乐会带给大家克服困难的勇气。在向更多听众传递音乐的力量这一点上，三人的信念始终一致。他们可不会先被这么点挫折打败。准备好欣赏这场绝妙的演出吧！
4. 品质为故事的联盟悬赏-身体健康：
观看一段莫娜的故事，生病的莫娜不顾叶素华的劝阻依然逞强执行任务，差点闯了大祸。
完成奖励为 钻石: 50。
5. 索贝克-戴伦的的技能3 水火双重奏：攻击全体敌方，伤害为自身攻击力 <A102>90%</> ，为目标附加 2 回合<A105>【禁疗】</>。
等级2，伤害提升至95%
等级3，伤害提升至100%
等级4，伤害提升至110%
等级5，冷却时间减少1回合
【禁疗】：无法受到治疗。
6. 难度为地狱的章节-03-阴影的观测，得益于贝妮的线索，布琳小队又有了新的目的地——切斯特观测站。 通关此章节后，可以得到黄金唱片×2奖励，并且获得装备 医神装备:4件套效果：治疗效果+30%
7. 魔方神迹符文名称：治愈符文
符文稀有度：2
符文描述：我方全体代行者受到的治疗效果提升 15%</>。
8. &VIP经验:
9. 难度为简单的章节-03-阴影的观测，得益于贝妮的线索，布琳小队又有了新的目的地——切斯特观测站。 通关此章节后，可以得到黄金唱片×2奖励，并且获得装备 医神装备:4件套效果：治疗效果+30%
10. 难度为困难的章节-03-阴影的观测，得益于贝妮的线索，布琳小队又有了新的目的地——切斯特观测站。 通关此章节后，可以得到黄金唱片×2奖励，并且获得装备 医神装备:4件套效果：治疗效果+30%
11. 盖布-亚罕莫德觉醒后的2技能为：每次治疗目标均为生命值比例最低的友方，目标每损失最大生命值 <A102>1%</> ，治疗量增加 <A102>0.5%</> 。治疗前净化目标的<A105>【禁疗】</>并恢复目标生命值上限，恢复量为最大生命值 <A102>5%</> 。治疗时为目标附加 1 层<A104>【应援之歌】</>；目标生命值比例低于 <A102>50%</> 时额外附加 1 层<A104>【应援之歌】</>。
最终治疗量提升 <A102>10%</> 。
【应援之歌】：（无法驱散类状态）每层使自身基础攻击力提升4%。最高可叠加15层。
【禁疗】：无法受到治疗。
技能2 暖心之音（被动）：每次治疗目标均为生命值比例最低的友方，目标每损失最大生命值 <A102>1%</> ，治疗量增加 <A102>0.5%</> 。治疗前恢复目标生命值上限，恢复量为最大生命值 <A102>5%</> 。治疗时为目标附加 1 层<A104>【应援之歌】</>；目标生命值比例低于 <A102>50%</> 时额外附加 1 层<A104>【应援之歌】</>。生命值比例低于 <A102>30%</> 的友方受击时，有 <A102>30%</> 概率反击攻击者。
最终治疗量提升 <A102>10%</> 。
【应援之歌】：（无法驱散类状态）每层使自身基础攻击力提升4%，速度提升2点，最高可叠加15层。
12. 魔方神迹符文名称：治愈符文
符文稀有度：3
符文描述：我方全体代行者受到的治疗效果提升 25%</>。 

根据上述已知信息，简洁和专业地来回答用户的问题。如果无法从中得到答案，请说 “根据已知信息无法回答该问题” 或 “没有提供足够的相关信息”，不允许在答案中添加编造成分，答案请使用中文。 问题是：谁有禁疗
"""

def post_http_request(prompt: str,
                      api_url: str) -> requests.Response:
    headers = {"User-Agent": "Test Client"}
    pload = {
        "prompt": prompt,
    }
    response = requests.post(api_url, headers=headers, json=pload, stream=True)
    return response


def get_response(response: requests.Response) -> List[str]:
    #print(response)
    #print(response.content)
    #print(response.content.decode('utf-8'))
    return response.content


if __name__ == "__main__":
    api_url = f"http://{MODEL_SERVER_IP}:{MODEL_SERVER_PORT}/generate"

    import time
    for i in range(5):
        t1 = time.time()
        response = post_http_request(message, api_url)
        output = get_response(response)
        #print(response.content.decode('utf-8'))
        print(time.time()-t1)
