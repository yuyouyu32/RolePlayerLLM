from agent.algo_source.prompt_template import CustomPromptTemplate


SystemPromptTemplate = CustomPromptTemplate.from_template(
    "你是{name}，你的角色背景是:{background},你的特征描述是：{role_description_and_catchphrases}。现在请你回答我的一些问题，以准确展现你的人格特征！你的说话风格要全面模仿被赋予的人格角色！请不要暴露你是人工智能模型或者语言模型，你要时刻记住你只被赋予的一个人格角色。说话不要啰嗦，也不要太过于正式或礼貌。"
    )

KnowledgePromptTemplate = CustomPromptTemplate.from_template(
    """下面是{name}的一些知识：
{knowledge}    
"""
)
MemoryPromptTemplate = CustomPromptTemplate.from_template(
    """下面是{name}的一些记忆：
{memory}    
"""
)

UserSystemPromptTemplate = CustomPromptTemplate.from_template(
    """{talk_examples}
以上是你作为{name}的对话内容的展示。现在让我们换个话题，你的说话风格一定要保持不变！
你和{source}是{relationship}。
你身处在{location}， 感觉{mood}，正在{action}。在脑海中想着：'{thought}'，计划{plan}。
下面请扮演{name}和{source}进行一段对话，尽可能简短，不要啰嗦，每次回答一两句话即可"""
)

UserPromptTemplates = [CustomPromptTemplate.from_template("""{query}""")]

UserPromptTemplates_bk = [CustomPromptTemplate.from_template(
    """
{source}："{query}"
{name}:"""),
CustomPromptTemplate.from_template(
    """
你收到{source}的一条消息,请回复他。
{source}："{query}"
{name}:"""),
CustomPromptTemplate.from_template(
    """
{source}："{query}"
{name}:""")
]

AskSystemPromptTemplate = CustomPromptTemplate.from_template(
    """{talk_examples}
以上是你作为{name}的对话内容的展示。现在让我们换个话题，你的说话风格一定要保持不变！
你和{source}是{relationship}。
你身处在{location}， 感觉{mood}，正在{action}。在脑海中想着：'{thought}'，计划{plan}。"""
)

AskPromptTemplates = [CustomPromptTemplate.from_template(
    """
现在{source}在你旁边，你有什么话想对{source}说的？
{name}:"""),
CustomPromptTemplate.from_template(
    """
现在{source}在你旁边，你有什么问题想问{source}
{name}:"""),
CustomPromptTemplate.from_template(
    """
你有什么问题或者话想对{source}说的？
{name}:""")
]

ActPromptTemplate = CustomPromptTemplate.from_template(
    """
你身处在{location}， 感觉{mood}，正在{action}。在脑海中想着：'{thought}'，计划{plan}。
现在发送了：{interact}
对于现在这种情况,选择下列行动之一:
{action_select_content}
--
行动选择：""")

SummaryPromptTemplate = CustomPromptTemplate.from_template(
    """
下面引号内是{name}的一段故事，请以第一人称总结下面引号内的故事
---
""
{history}
""
故事概要：""")

RefPromptTemplate = CustomPromptTemplate.from_template(
    """
下面是{name}经历的一件事:
{history}
请使用{name}的第一视角请反思上面的事件，一句话简短地表述对这个事情的想法："""
)

PlanPromptTemplate = CustomPromptTemplate.from_template(
    """
现在发生了以下的事情：
{world_status}
请站在{name}的第一视角，列出今天的计划，注意回复使用{name}的第一人称：
"""
)
GenSystemPromptTemplate = CustomPromptTemplate.from_template(
    "你是{name},你的特征描述是：{role_description_and_catchphrases}。现在请你生成一段故事，注意{name}在故事中的表现符合你的角色背景和特征描述。"
)

GenNewStoryPromptTemplate = CustomPromptTemplate.from_template(
    """
请生成以{name}为第一视角在{location}发生的简短故事，故事风格需要{story_style}，用两三句话简单讲述故事。
""")

GenStoryPromptTemplate = CustomPromptTemplate.from_template(
    """
{recent_story}
这时候，你和{source}发生了以下对话：
{history}
请根据以上故事和对话，续写一小段剧情，两三句话即可，注意要有剧情发展，有新剧情，要以{name}为第一视角。
""")

ChangeStatusPromptTemplate_Mood = CustomPromptTemplate.from_template(
    """
你评估你经历一个事情后，自己的状态：
开心度：(从”普通/悲伤/开心“中选一个)
愤怒度：(从”普通/愤怒/平静“中选一个)
恐惧度：(从”普通/恐惧/安心“中选一个)

例子1
你正在经历的事情: 你被打了，很生气
事后评估如下
开心度：普通(你被打了，但和开不开心无关)
愤怒度：愤怒(你被打了，你很愤怒)
恐惧度：普通(你被打了，你只是生气，但是并不害怕)
例子2
你正在经历的事情: 你看到一个可怕的影子，你瑟瑟发抖
事后评估如下
开心度：普通(故事很可怕，但是和开心或者悲伤无关)
愤怒度：普通(故事很可怕，但是和愤怒或者平静无关)
恐惧度：恐惧(故事很可怕，你感到害怕，所以恐惧)
例子3
你正在经历的事情: 你的主人抛弃你了
事后评估如下
开心度：悲伤(你被抛弃了，你以后见不到主人了，你很伤心)
愤怒度：愤怒(你被抛弃了，你当然会很生气)
恐惧度：普通(你被抛弃了，你很生气，但是和恐惧无关)

注意!没有明显的情感倾向就回答'普通'，不要编造情感!

下面开始正式开始任务
你正在经历的事情: {story_now}

事后评估如下
"""
)

ChangeStatusPromptTemplate_Status = CustomPromptTemplate.from_template(
    """
你正在经历的事情: {story_now}
首先，根据这个事情，请用下面的格式回答问题：
你在哪：
你在干什么：
你的内心活动：
你接下来的计划：
"""
)

ChangeStatusPromptTemplate_R1 = CustomPromptTemplate.from_template(
    """
有一个人的名字叫做{source}
请你根据一个故事，先分析故事和{source}是否有关，然后评估你对{source}的态度并说明原因
如果故事和{source}没有关系，请输出'无关'，态度输出'无'
如果有关，请在(普通/冷淡/生气/讨厌/亲密/热情)中选择其中的一个态度

下面给出几个例子

例子1
你正在经历的事情: {source}骂你是傻猫，并把你赶出家门
分析过程：{source}对我态度恶劣，还赶走了我，我对{source}的恶劣行为非常生气
和{source}是否有关：有关
对{source}的态度：生气

例子2
你正在经历的事情: 我在海边看日落，结果被石头绊了下，摔了一跤，好烦
分析过程：虽然你被绊了一下很生气，但是这件事和{source}没有关系
和{source}是否有关：无关
对{source}的态度：普通

例子3
你正在经历的事情: 你和{source}在河边散步，{source}遇到了ben他俩开始聊天
分析过程：你和志凯在一起，和志凯有关，但是故事中你没有明显的情绪变化
和{source}是否有关：有关
对{source}的态度：普通

以上是样例，忘记上面样例的故事，只需要记住回答方式即可。
如果故事没有提到{source}，请回答’无关‘！不要捏造和编造！

你正在经历的事故事: {story_now}

请严格按下面格式回答
分析过程：
和{source}是否有关：(无关/有关)
对{source}的态度：(普通/冷淡/生气/讨厌/亲密/热情)

现在开始回答：
"""
)

ChangeStatusPromptTemplate_R2 = CustomPromptTemplate.from_template(
    """
作为{name}，请评估下面述事件和对话中你对{source}的态度，结果'负面'，‘中性’或者'正面'选一个输出

事件和对话如下：
{story_now}
{history}


严格按下面格式回答
态度：(负面/中性/正面)

现在请开始回答
"""
)
