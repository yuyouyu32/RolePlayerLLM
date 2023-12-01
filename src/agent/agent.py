import datetime
import re
from typing import List, Any, Dict
from util.logging import logger
from agent.config import *
from agent.model_client.model_client import ModelClient
from agent.vector_source.knowledge import Knowledge
from agent.vector_source.memory import Memory
from agent.vector_source.document import Document
from agent.stream_source.history import History 
from agent.kv_source.persona import Persona
from agent.kv_source.status import AgentStatus
from agent.query_analysis import QueryAnalysis 

from model_server.config import MODEL_SERVER_PORT
from util.session import Session
from agent.kv_source.user import User
from agent.stream_source.event import Event 
from agent.algo_source.algo import AlgoBase 
from agent.kv_source.status import NUMERIC_MAP, STATUS_CHANGE_CONFIG


class Agent():
    def __init__(self, custom_algo: AlgoBase = None):
        """
        Description:
            init chatbot
        Input:
            idx: str, for chatbot to identify which user's history to use
        """
        self.qa = QueryAnalysis()

        self.model = ModelClient(MODEL_SERVER_PORT)  # LLM
        # DB
        self.user =  User(UserInfoDBconfig) # Usr information key-value DB
        self.persona = Persona(PersonaDBConfig) # constant key-value DB
        self.status = AgentStatus(StatusDBConfig) # variable key-value DB 

        self.history = History(HistoryDBConfig) # Time Series Database
        self.knowledge = Knowledge(KnowledgeDBConfig)  # constant vectorDB
        self.memory = Memory(MemoryDBConfig)     # variable vectorDB

        if custom_algo:
            self.algo = custom_algo
        else:
            self.algo = AlgoBase()

        self.methods = {
            "remember": self.remember,
            "plan": self.plan,
            "reflect": self.reflect,
            "act": self.act,
            "chat": self.chat,
            "ask": self.ask,
            "new_scenario": self.new_scenario,
            "step": self.step
        }

    def set_bot(self, config: Dict, session: Session):
        self.config = config
        self.sess = session

    def session_init(self):
        if self.user.id_exists(self.sess) and self.user.get_status(self.sess):
            logger.info("User already exists and all table have been created.")
        else:
            self.user.insert_user(self.sess)
            self.persona.insert_user(self.sess)
            self.status.insert_user(self.sess)
            self.knowledge.create(self.sess)
            self.memory.create(self.sess)
            self.user.set_status(self.sess)

    def show_session_db(self):
        """
        Description:
            for debug, check all data in DB
        """
        max_num = 10
        print("persona " + "=="*5)
        self.persona.show(self.sess)
        print("satus " + "=="*5)
        self.status.show(self.sess)
        print("history " + "=="*5)
        self.history.show(self.sess, max_num)
        #print("knowledge " + "=="*5)
        #self.knowledge.show(self.sess, max_num)
        #print("memory " + "=="*5)
        #self.memory.show(self.sess, max_num)

    def clear(self):
        try:
            self.persona.clear(self.sess)
            self.history.clear(self.sess)
            self.status.clear(self.sess)
            self.knowledge.clear(self.sess)
            self.memory.clear(self.sess)
            self.user.clear(self.sess)
        except Exception as e:
            print(e)

    def add_knowledge(self, new_knowledges: List[str]):
        """
        Description:
            force agent to get new knowledge {could be used for story talker}
        """
        new_knowledge_docs = []
        for new_knowledge in new_knowledges:
            new_knowledge_doc = Document(dtime = datetime.datetime.now(),
                                  content = new_knowledge,
                                  dtype = "new_knowledge")
            new_knowledge_docs.append(new_knowledge_doc)
        self.knowledge.add_source(self.sess, new_knowledge_docs)

    def _add_context(self, q_o: str) -> str:
        """
        Description:
            add history q_a pair context to query
        Input:
            q_o: str, query
        output:
            query_with_context: str, response with context
        """
        # TODO
        return q_o

    def _process_obs(self, observation: Dict[str, Any]):
        """
        Description:
            process query for retriever
        """
        if "query" in observation: 
            search_query = observation["query"]
            # process search query info for retrievers 
            if self.config["use_knowledge"] or self.config["use_memory"]:
                search_query_with_context = self._add_context(search_query)
                observation['search_query_info'] = self.qa.process(search_query_with_context)
        elif "interact" in observation: 
            search_query = observation["interact"]
            # process search query info for retrievers 
            if self.config["use_knowledge"] or self.config["use_memory"]:
                search_query_with_context = self._add_context(search_query)
                observation['search_query_info'] = self.qa.process(search_query_with_context)

    def _process_rsp(self, rsp: str, rsp_type: str, observation: Dict[str, Any], candidate_actions: List[str] = None) -> Dict[str, str]:
        """
        Description:
            process respond to adapt game-core
        """
        rsp_dict = {}
        status = self._requirement_collect({"status": {}})['status']
        if rsp_type == 'chat':
            rsp_dict["type"] = rsp_type 
            rsp_dict["content"] = rsp
            rsp_dict['status'] = status
            return rsp_dict 
        else:
            # TODO
            rsp_dict["type"] = rsp_type 
            rsp_dict["content"] = rsp
            rsp_dict['status'] = status
            return rsp_dict 

    def _requirement_collect(self, requirement: Dict[str, Any], observation: Dict[str, Any] = None) -> dict:
        """
        Description:
           collect all required infomation for building prompt
        """
        collections = {}
        for r,v in requirement.items():
            if r == "query": collections[r] = observation["query"]
            elif r == "source": collections[r] = observation["source"]
            elif r == "interact": collections[r] = observation["interact"]
            elif r == "persona": collections[r] = self.persona.get(self.sess)
            elif r == "knowledge": 
                if not self.config["use_knowledge"]:
                    continue
                knowledge_content = self.knowledge.get_source(self.sess, observation["search_query_info"], keep_max_k=v["keep_num"])
                collections[r] = knowledge_content
            elif r == "memory": 
                if not self.config["use_memory"]:
                    continue
                memory_content = self.memory.get_source(self.sess, observation["search_query_info"], keep_max_k=v["keep_num"])
                collections[r] = memory_content
            elif r == "plan": collections[r] = self.status.get_plan_descri(self.sess)
            elif r == "status": collections[r] = self.status.get(self.sess)
            elif r == "candidate_actions": collections[r] = observation["candidate_actions"]
            elif r == "history": 
                history = self.history.get(self.sess, event_types=['chat', 'act', 'ref'], keep_num=v["keep_num"])
                collections[r] = history 
                if v["reset_step"]: self.history.set_step()
            elif r == "world_status": collections[r] = observation["world_status"]
            else:
                raise(f"{r} not define in requirement collector")
        return collections

    def remember(self, story : Dict[str, str] = None):
        """
        Description:
           insert summary of story(data in questDB) to memory(vectorDB)
        """
        logger.info("==="*3 + "SUMMARY" +"==="*3)
        if story:
            new_memory = Document(dtime_str = story["time"],
                                  content = story["content"],
                                  dtype = "story_summary")
        else:
            # summary
            prompt_content_requirement = self.algo.prompt_requirement["summary"] 
            prompt_content = self._requirement_collect(prompt_content_requirement)
            assert "history" in prompt_content
            system_prompt, instruction = self.algo.build_prompt("summary", prompt_content)

            logger.info("\n*REMEMBER PROMPT*\nsystem_prompt:{}\nprompt:\n{}\n".format(system_prompt, instruction))

            message = {"system_prompt": system_prompt, "instruction": instruction, "histories": []}
            story_summary = self.model.predict(message)

            logger.info(f"gen summary: {story_summary}\n")
            last_event = prompt_content["history"][-1]

            new_memory = Document(dtime = last_event.dtime,
                                  content = story_summary,
                                  dtype = "story_summary")
        self.memory.add_source(self.sess, [new_memory])

    def plan(self, observation: Dict[str, Any], plan_type: int = 0):
        """
        Description:
           make a longterm plan (build prompt to change status(k-v DB))
        """
        logger.info("==="*3 + "PLAN" +"==="*3)
        prompt_content_requirement = self.algo.prompt_requirement["plan"] 
        prompt_content = self._requirement_collect(prompt_content_requirement, observation)
        system_prompt, instruction = self.algo.build_prompt("plan", prompt_content)

        logger.info("\n*PLAN PROMPT*\nsystem_prompt:{}\nprompt:\n{}\n".format(system_prompt, instruction))

        message = {"system_prompt": system_prompt, "instruction": instruction, "histories": []}
        plan = self.model.predict(message)
        logger.info(f'gen plan: {plan}\n')

        self.status.set_status(self.sess, "plan", plan)

    def reflect(self, keep_num: int = 10, reflect_type: int = 0):
        """
        Description:
           build prompt to add sth to history(quest DB)
        """
        logger.info("==="*3 + "REFLECT" +"==="*3)
        prompt_content_requirement = self.algo.prompt_requirement["ref"] 
        prompt_content = self._requirement_collect(prompt_content_requirement)
        assert "history" in prompt_content and len(prompt_content["history"])>0
        system_prompt, instruction = self.algo.build_prompt("ref", prompt_content)

        logger.info("\n*REFELECT PROMPT*\nsystem_prompt:{}\nprompt:\n{}\n".format(system_prompt, instruction))

        message = {"system_prompt": system_prompt, "instruction": instruction, "histories": []}
        reflection = self.model.predict(message)
        logger.info(f'gen reflection: {reflection}\n')

        last_event = prompt_content["history"][-1]
        new_reflect_event = Event(ref = reflection,
                          dtime = last_event.dtime,
                          event_type = "ref")
        self.history.add(self.sess, new_reflect_event)

    def act(self, observation: Dict[str, Any]) -> Dict[str, str]:
        """
        Description:
           respond to interact
        """
        logger.info("==="*3 + "ACT" +"==="*3)
        if "interact" not in observation:
            return None
        self._process_obs(observation)

        prompt_content_requirement = self.algo.prompt_requirement["act"] 

        prompt_content = self._requirement_collect(prompt_content_requirement, observation)
        system_prompt, instruction = self.algo.build_prompt("act", prompt_content)

        logger.info("\n*ACT PROMPT*\nsystem_prompt:{}\nprompt:\n{}\n".format(system_prompt, instruction))

        message = {"system_prompt": system_prompt, "instruction": instruction, "histories": []}
        action = self.model.predict(message)
        logger.info(f'gen action: {action}\n')

        new_act_event = Event(source = observation["source"],
                          obs = observation["interact"],
                          rsp = action,
                          dtime_str = observation["time"],
                          event_type = "act")
        self.history.add(self.sess, new_act_event)
        
        return self._process_rsp(action, 'act', observation)

    def chat(self, observation: Dict[str, Any]) -> Dict[str, str]:
        """
        Description:
           respond to chat
        """
        logger.info("==="*3 + "CHAT" +"==="*3)
        if "query" not in observation:
            return None

        self._process_obs(observation)

        prompt_content_requirement = self.algo.prompt_requirement["chat"] 

        prompt_content = self._requirement_collect(prompt_content_requirement, observation)
        system_prompt, instruction = self.algo.build_prompt("chat", prompt_content)
        
        chat_histories = []
        if self.config["use_chat_history"]:
            chat_histories = self.history.get(self.sess, event_types=['chat'], keep_num=self.algo.chat_history_num, postprocess = "chat_pair")
        logger.info("histories:{}\nsystem_prompt:{}\nprompt:\n{}\n".format(chat_histories, system_prompt, instruction))

        message = {"system_prompt": system_prompt, "instruction": instruction, "histories": chat_histories, "temperature": 0.6}
        response = self.model.predict(message)
        logger.info(f'gen response: {response}\n')

        new_chat_event = Event(source = observation["source"],
                          obs = observation["query"],
                          rsp = response,
                          dtime_str = observation["time"],
                          event_type = "chat")
        self.history.add(self.sess, new_chat_event)
        return self._process_rsp(response, 'chat', observation)

    def ask(self, observation: Dict[str, Any]) -> Dict[str, str]:
        """
        Description:
           respond to chat
        """
        logger.info("==="*3 + "CHAT" +"==="*3)
        if "query" not in observation:
            return None

        self._process_obs(observation)

        prompt_content_requirement = self.algo.prompt_requirement["chat"] 

        prompt_content = self._requirement_collect(prompt_content_requirement, observation)
        system_prompt, instruction = self.algo.build_prompt("ask", prompt_content)
        
        chat_histories = []
        if self.config["use_chat_history"]:
            chat_histories = self.history.get(self.sess, event_types=['chat'], keep_num=self.algo.chat_history_num, postprocess = "chat_pair")
        logger.info("histories:{}\nsystem_prompt:{}\nprompt:\n{}\n".format(chat_histories, system_prompt, instruction))

        message = {"system_prompt": system_prompt, "instruction": instruction, "histories": chat_histories, "temperature": 0.9}
        response = self.model.predict(message)
        logger.info(f'gen response: {response}\n')

        new_chat_event = Event(source = observation["source"],
                          obs = '',
                          rsp = response,
                          dtime_str = observation["time"],
                          event_type = "chat")
        self.history.add(self.sess, new_chat_event)
        return self._process_rsp(response, 'chat', observation)

    def new_scenario(self, observation):
        # update old 
        prompt_content_requirement = self.algo.prompt_requirement["create_memory"] 
        prompt_content = self._requirement_collect(prompt_content_requirement, observation)
        story_summary = self.algo.construct_memory_content(prompt_content)
        story =  {"time": observation["time"],
                  "content": story_summary}
        logger.info(f'story_summary: {story_summary}\n')
        self.remember(story)

        # update new 
        self.generate_story(observation, is_beginning = True)
        self.change_status(observation)

        # clear but not remove history
        self.history.clear(self.sess)
        return self._process_rsp("", 'new_scenario', observation)

    def step(self, observation):
        # update old 
        prompt_content_requirement = self.algo.prompt_requirement["create_memory"] 
        prompt_content = self._requirement_collect(prompt_content_requirement, observation)
        story_summary = self.algo.construct_memory_content(prompt_content)
        story =  {"time": observation["time"],
                  "content": story_summary}
        logger.info(f'story_summary: {story_summary}\n')
        self.remember(story)

        # update new 
        self.change_status(observation, ctypes = ["relationship"])
        self.generate_story(observation, is_beginning = False)
        self.change_status(observation, ctypes = ["mood", "status"])

        # clear but not remove history
        self.history.clear(self.sess)
        return self._process_rsp("", 'step', observation)
    
    def generate_story(self, observation, is_beginning = True):
        """
        Description:
           generate story
        """
        logger.info("==="*3 + "GENERATE STORY" +"==="*3)
        prompt_content_requirement = self.algo.prompt_requirement["generate_story"] 
        prompt_content = self._requirement_collect(prompt_content_requirement, observation)
        system_prompt, instruction = self.algo.build_prompt("generate_story", prompt_content, is_beginning=is_beginning)

        logger.info("\n*GENERATE STORY PROMPT*\nsystem_prompt:{}\nprompt:\n{}\n".format(system_prompt, instruction))

        message = {"system_prompt": system_prompt, "instruction": instruction, "histories": []}
        story = self.model.predict(message)
        logger.info(f'gen story: {story}\n')

        new_story_event = Event(source = observation["source"],
                          rsp = story,
                          dtime_str = observation["time"],
                          event_type = "generate_story")
        self.history.add(self.sess, new_story_event)
        if is_beginning:
            self.status.set_status(self.sess, "all_story", story)
        else:
            self.status.set_status(self.sess, "all_story", prompt_content['status']['all_story']+"\n"+story)
        self.status.set_status(self.sess, "recent_story", story)
        return self._process_rsp(story, 'story', observation)
    
    def change_status(self, observation, ctypes = STATUS_CHANGE_CONFIG.keys()):
        """
        Description:
           ask LLM to change status
        """
        logger.info("==="*3 + "CHANGE STATUS" +"==="*3)
        assert "status" in self.algo.prompt_requirement["change_status"]
        prompt_content_requirement = self.algo.prompt_requirement["change_status"] 
        prompt_content = self._requirement_collect(prompt_content_requirement, observation)
        pre_status = prompt_content["status"]

        for ctype in ctypes:
            system_prompt, instruction = self.algo.build_prompt("change_status", prompt_content, template_type=ctype)

            logger.info("\n*CHANGE STATUS PROMPT*\nsystem_prompt:{}\nprompt:\n{}\n".format(system_prompt, instruction))

            message = {"system_prompt": system_prompt, "instruction": instruction, "histories": []}
            new_status_descri = self.model.predict(message)
            logger.info(f'new status descri: {new_status_descri}\n')

            new_status_descri += "\n"
            for status_key, status_change_config in STATUS_CHANGE_CONFIG[ctype].items():
                re_patterns = status_change_config['re']
                for re_pattern in re_patterns:
                    status_descri_list = re.findall(re_pattern, new_status_descri)
                    if len(status_descri_list) != 0: break
                if len(status_descri_list) != 1:
                    logger.warning(f'change status {status_key} fail!')
                    continue
                status_descri = status_descri_list[0]

                def status_postprocess(key, pre_val, cur_descri, config):
                    try:
                        if config['postprocess_type'] == None:
                            val = cur_descri 
                        elif config['postprocess_type'] == "map":
                            val = config['map'][cur_descri] 
                        else:
                            raise(f'unknow postprocess_type')

                        if config['update_method'] == "update":
                            pass
                        elif config['update_method'] == "add":
                            val = pre_val + val
                            min_v, max_v = min(NUMERIC_MAP[key].keys()), max(NUMERIC_MAP[key].keys()) 
                            val = min(val, max_v)
                            val = max(val, min_v)
                        else:
                            raise(f'unknow update_method')

                        return val
                    except Exception as e:
                        logger.warning(str(e))
                        return None

                val = status_postprocess(status_key, pre_status[status_key], status_descri, status_change_config)
                if val != None:
                    self.status.set_status(self.sess, status_key, val)
                else:
                    logger.warning(f'status_postprocess {status_key} with value {status_descri} fail')
        return self._process_rsp('', 'None', observation)
        


def unit_test():
    import datetime
    session = Session(user_idx="testid123", prototype_id='maomao', user_name="ben")
    test_config = {"use_knowledge": True,
                   "use_memory": True,
                   "use_chat_history": True}
    bot = Agent()
    bot.set_bot(test_config, session)
    bot.clear()
    bot.session_init()
    #observation = {"query": "哟~新联系人！你是谁呀？", "source": "ben", "time": str(datetime.datetime.now())}
    #test_rsp = bot.chat(observation)
    #observation = {"query": "原来是毛毛啊！你喜欢我吗？", "source": "ben", "time": str(datetime.datetime.now())}
    #test_rsp = bot.chat(observation)
    #observation = {"query": "你认识kenny吗？", "source": "ben", "time": str(datetime.datetime.now())}
    #test_rsp = bot.chat(observation)
    #observation = {"query": "你在干嘛呢？", "source": "ben", "time": str(datetime.datetime.now())}
    #test_rsp = bot.chat(observation)
    observation = {"source": "ben", "time": str(datetime.datetime.now())}
    test_rsp = bot.new_scenario(observation)
    observation = {"source": "ben", "time": str(datetime.datetime.now())}
    test_rsp = bot.step(observation)
    observation = {"query": "", "source": "ben", "time": str(datetime.datetime.now())}
    test_rsp = bot.ask(observation)
    observation = {"query": "你在干嘛呢？", "source": "ben", "time": str(datetime.datetime.now())}
    test_rsp = bot.chat(observation)
    # observation = {"interact": "你被ben打了一下", 
    #                "source": "ben", 
    #                "candidate_actions":["打回去", "躲闪", "向ben求援"], 
    #                "time": str(datetime.datetime.now())}
    # test_rsp = bot.act(observation)
    # test_rsp = bot.reflect(4)

    # test_rsp = bot.remember()

    # print("==="*5)
    # print("第二天到了")
    # observation = {"world_status": "今天西湖下了暴雨", "time": str(datetime.datetime.now())}
    # test_rsp = bot.plan(observation)

    bot.clear()

def unit_test_interact():
    import datetime
    session = Session(user_idx="testid123", prototype_id='maomao', user_name="ben")
    test_config = {"use_knowledge": True,
                   "use_memory": True,
                   "use_chat_history": True}
    bot = Agent()
    bot.set_bot(test_config, session)
    bot.clear()
    bot.session_init()
    while 1:
        content = input("请输入问题: ")
        if content == "@@":
            observation = {"source": "志凯", "time": str(datetime.datetime.now())}
            test_rsp = bot.new_scenario(observation)
        elif content == "##":
            observation = {"source": "志凯", "time": str(datetime.datetime.now())}
            test_rsp = bot.step(observation)
        elif content == "ask":
            observation = {"query": "", "source": "志凯", "time": str(datetime.datetime.now())}
            test_rsp = bot.ask(observation)
        else:
            observation = {"query": content, "source": "志凯", "time": str(datetime.datetime.now())}
            test_rsp = bot.chat(observation)


if __name__ == "__main__":
    #unit_test()
    unit_test_interact()
