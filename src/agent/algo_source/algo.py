from agent.algo_source.prompts import *
import random

class AlgoBase:
    """
    Define sepicific algorithm pipeline, including prompt build function and choose models
    """
    def __init__(self,):
        """
        Define requirement of each prompt builder
        """
        self.chat_history_num = 3   # length of chat_histories in model.predict({"system_prompt": system_prompt, "instruction": instruction, "histories": chat_histories})
        self.prompt_requirement = {"chat": {"query":{}, "persona":{}, "knowledge":{"keep_num":2}, "memory":{"keep_num":2}, "plan":{}, "status":{}, "source": {}},
                                   "act": {"interact":{}, "persona":{}, "knowledge":{"keep_num":2}, "memory":{"keep_num":2}, "plan":{}, "status":{}, "candidate_actions":{}},
                                   "ref": {"history":{"keep_num":2, "reset_step": False}, "persona":{}, "plan":{}, "status":{}},
                                   "summary": {"persona":{}, "history":{"keep_num":-1, "reset_step": True}},
                                   "plan":{"world_status":{}, "persona":{}, "status":{}},
                                   "generate_story": {"history":{"keep_num":6, "reset_step": False}, "persona":{}, "status":{}, "source": {}},
                                   "change_status": {"persona":{}, "status":{}, "source": {}, "history":{"keep_num":3, "reset_step": False}},
                                   "create_memory": {"history":{"keep_num":2, "reset_step": False}, "status":{}}}
                                   
       
    def build_prompt(self,prompt_type, prompt_content, **kwargs):
        """
        Router
        """
        if prompt_type == "chat":
            return self._build_chat_prompt(prompt_content)
        elif prompt_type == "ask":
            return self._build_ask_prompt(prompt_content)
        elif prompt_type == "act":
            return self._build_act_prompt(prompt_content)
        elif prompt_type == "ref":
            return self._build_reflect_prompt(prompt_content)
        elif prompt_type == "plan":
            return self._build_plan_prompt(prompt_content)
        elif prompt_type == "summary":
            return self._build_summary_prompt(prompt_content)
        elif prompt_type == 'generate_story':
            return self._build_generate_story_prompt(prompt_content, **kwargs)
        elif prompt_type == 'change_status':
            return self._build_change_status_prompt(prompt_content, **kwargs)
    
    def _build_system_prmopt(self, prompt_content):
        """
        Build system prompt
        """
        system_prompt = SystemPromptTemplate.format(name=prompt_content["persona"]["name"], background=prompt_content["persona"]["background"], role_description_and_catchphrases=prompt_content["persona"]["persona"] + ' ' + prompt_content["persona"]["style"])
        return system_prompt
    
    def _get_knowledge_memory(self, prompt_content: dict):
        temp_prompt = ''
        if prompt_content.get('knowledge', None) and prompt_content["knowledge"]:
            knowledge_part = KnowledgePromptTemplate.format(name=prompt_content["persona"]["name"], knowledge=prompt_content["knowledge"])
            temp_prompt += knowledge_part
      
        if prompt_content.get('memory', None) and prompt_content["memory"]:
            memory_part = MemoryPromptTemplate.format(name=prompt_content["persona"]["name"], memory=prompt_content["memory"])
            temp_prompt += memory_part

        return temp_prompt
    
    def _get_history(self, prompt_content):
        history_descri = ''
        name = prompt_content["persona"]["name"]
        for event in prompt_content["history"]:
            if event.event_type == "chat":
                event_descri = f'{event.source}说:"{event.obs}"\n{name}说:"{event.rsp}"\n' 
            elif event.event_type == "ref":
                event_descri = f'{name}想:{event.ref}' 
            elif event.event_type == "act":
                event_descri = f'{event.obs}\n{name}{event.rsp}' 
            history_descri += "\n" + event_descri
        return history_descri
    
    def _build_chat_prompt(self, prompt_content):
        system_prompt = self._build_system_prmopt(prompt_content)

        system_prompt += self._get_knowledge_memory(prompt_content)

        talk_examples = '\n'.join(random.sample(prompt_content["persona"]["talk_examples"].split('\n'), 3))
        mood = "，".join([prompt_content["status"]["happy_descri"], prompt_content["status"]["angry_descri"], prompt_content["status"]["fear_descri"]])

        system_prompt += UserSystemPromptTemplate.format(talk_examples=talk_examples, mood=mood, location=prompt_content["status"]["location"], action=prompt_content["status"]["action"], thought=prompt_content["status"]["thought"], plan=prompt_content["status"]["plan"], name=prompt_content["persona"]["name"], source=prompt_content["source"], relationship=prompt_content["status"]["relationship_descri"])

        pt = random.choice(UserPromptTemplates) 
        chat_prompt = pt.format(query=prompt_content["query"])
        return system_prompt, chat_prompt
    
    def _build_ask_prompt(self, prompt_content):
        system_prompt = self._build_system_prmopt(prompt_content)

        system_prompt += self._get_knowledge_memory(prompt_content)

        talk_examples = '\n'.join(random.sample(prompt_content["persona"]["talk_examples"].split('\n'), 3))
        mood = "，".join([prompt_content["status"]["happy_descri"], prompt_content["status"]["angry_descri"], prompt_content["status"]["fear_descri"]])

        system_prompt += AskSystemPromptTemplate.format(talk_examples=talk_examples, mood=mood, location=prompt_content["status"]["location"], action=prompt_content["status"]["action"], thought=prompt_content["status"]["thought"], plan=prompt_content["status"]["plan"], name=prompt_content["persona"]["name"], source=prompt_content["source"], relationship=prompt_content["status"]["relationship_descri"])

        pt = random.choice(AskPromptTemplates) 
        ask_prompt = pt.format(source=prompt_content["source"], name=prompt_content["persona"]["name"])
        return system_prompt, ask_prompt
    
    
    def _build_act_prompt(self, prompt_content):
        action_select_content = [f'{idx}.{action}' for idx, action in enumerate(prompt_content["candidate_actions"])]

        system_prompt = self._build_system_prmopt(prompt_content)
        act_prompt = self._get_knowledge_memory(prompt_content)
    

        mood = "，".join([prompt_content["status"]["happy_descri"], prompt_content["status"]["angry_descri"], prompt_content["status"]["fear_descri"]])
        tail_part = ActPromptTemplate.format(mood=mood, location=prompt_content["status"]["location"], action=prompt_content["status"]["action"], thought=prompt_content["status"]["thought"], plan=prompt_content["status"]["plan"], interact=prompt_content["interact"], action_select_content='\n'.join(action_select_content))
        act_prompt += tail_part 

        return system_prompt, act_prompt
    
    def _build_summary_prompt(self, prompt_content):
        history_descri = self._get_history(prompt_content)
    
        system_prompt = self._build_system_prmopt(prompt_content)
    
        summary_prompt = SummaryPromptTemplate.format(name=prompt_content["persona"]["name"], history=history_descri)
        return system_prompt, summary_prompt
    
    def _build_reflect_prompt(self, prompt_content):
        history_descri = self._get_history(prompt_content)

        system_prompt = self._build_system_prmopt(prompt_content)

        reflect_prompt = RefPromptTemplate.format(name=prompt_content["persona"]["name"], history=history_descri)
        return system_prompt, reflect_prompt
    
    def _build_plan_prompt(self, prompt_content):
        system_prompt = self._build_system_prmopt(prompt_content)
    
        plan_prompt = PlanPromptTemplate.format(name=prompt_content["persona"]["name"], world_status=prompt_content["world_status"])
        return system_prompt, plan_prompt

    def _build_generate_story_prompt(self, prompt_content, **kwargs):
        """
        Build generate story prompt
        """
        is_beginning = kwargs['is_beginning']
        if is_beginning:
            system_prompt = GenSystemPromptTemplate.format(name=prompt_content["persona"]["name"], role_description_and_catchphrases=prompt_content["persona"]["persona"] + ' ' + prompt_content["persona"]["style"])
            generate_story_prompt = GenNewStoryPromptTemplate.format(name=prompt_content["persona"]["name"], location=random.choice(['西湖', '海边', '家里', '草原', '沙漠', '上海', '北京', '河边','猫窝','草地','公园']), story_style=random.choice(['幽默', '狗血', '悲伤', '浪漫', '愉悦', '搞笑', '出糗', '恐怖', '让人气愤', '抓狂', '可怕']))
        else:
            history_descri = self._get_history(prompt_content)
            system_prompt = GenSystemPromptTemplate.format(name=prompt_content["persona"]["name"], role_description_and_catchphrases=prompt_content["persona"]["persona"] + ' ' + prompt_content["persona"]["style"])
            generate_story_prompt = GenStoryPromptTemplate.format(name=prompt_content["persona"]["name"], source=prompt_content["source"], history=history_descri, recent_story=prompt_content["status"]["all_story"])
        return system_prompt, generate_story_prompt

    def _build_change_status_prompt(self, prompt_content, **kwargs):
        """
        Build generate story prompt
        """
        template_type = kwargs['template_type']
        system_prompt = GenSystemPromptTemplate.format(name=prompt_content["persona"]["name"], role_description_and_catchphrases=prompt_content["persona"]["persona"] + ' ' + prompt_content["persona"]["style"])


        if template_type == 'mood':
            change_status_prompt = ChangeStatusPromptTemplate_Mood.format(story_now=prompt_content["status"]["recent_story"])
        elif template_type == 'status':
            change_status_prompt = ChangeStatusPromptTemplate_Status.format(story_now=prompt_content["status"]["recent_story"])
        elif template_type == 'relationship':
            history_descri = self._get_history(prompt_content)
            #change_status_prompt = ChangeStatusPromptTemplate_R2.format(history=history_descri, source=prompt_content["source"])
            change_status_prompt = ChangeStatusPromptTemplate_R2.format(name=prompt_content["persona"]["name"], history=history_descri, source=prompt_content["source"], story_now=prompt_content["status"]["recent_story"])
        return system_prompt, change_status_prompt

    def construct_memory_content(self, prompt_content):
        """
        construct new memory 
        """
        mood = "，".join([prompt_content["status"]["happy_descri"], prompt_content["status"]["angry_descri"], prompt_content["status"]["fear_descri"]])
        story_summary = f'前段时间，你在{prompt_content["status"]["location"]}，{prompt_content["status"]["action"]}，当时你感觉{mood}，当时你心想：{prompt_content["status"]["thought"]}'
        return story_summary 

