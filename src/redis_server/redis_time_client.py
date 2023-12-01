from .redis_base import Redis_Base_Client
import redis
from typing import Dict, Any, List, Union, Awaitable
from agent.stream_source.event import Event
import json
import datetime

class RedisTimeClient(Redis_Base_Client):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
    
    def insert_data(self, table_name: str, event: Event) -> Union[Awaitable[int], int]:
        """
        Description:
            Insert data into Redis.
        Args:
            table_name: The name of table.
            event: The event of table.
        Return:
            Returns the number of fields that were added.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            timestamp = event.dtime.timestamp()
            hash_key = f"{table_name}:{timestamp}"
            hash_fields = {
                'source': str(event.source),
                'observation': str(event.obs),
                'response': str(event.rsp),
                'reflection': str(event.ref),
                'event_type': str(event.event_type)
            }
            
            ret = conn.hset(hash_key, mapping=hash_fields)
            conn.sadd('table_names', table_name)
            # For timestamp sort
            zset_key = f"{table_name}:{event.event_type}_sorted"
            conn.zadd(zset_key, {str(timestamp): timestamp})
            return ret
        
    def search(self, table_name:str, event_types: tuple, keep_num: int) -> List[Event]:
        """
        Description:
            search data from QuestDB QA table
        Input:
            idx: str, for chatbot to identify which user's memory to use
        Output:
            history: List[Event], the history of this chatid
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            all_data: List[Event] = []
            for event_type in event_types:
                zset_key = f"{table_name}:{event_type}_sorted"
                
                sorted_timestamps = conn.zrevrange(zset_key, 0, keep_num - 1)
                
                for timestamp in sorted_timestamps:
                    hash_key = f"{table_name}:{timestamp}"
                    data = conn.hgetall(hash_key)
                    data['timestamp'] = timestamp
                    event = Event(source = data['source'], \
                                  obs = data['observation'], \
                                  rsp = data['response'], \
                                  ref = data['reflection'], \
                                  event_type = data['event_type'], \
                                  dtime = datetime.datetime.fromtimestamp(float(timestamp)), \
                                  dtime_str = datetime.datetime.fromtimestamp(float(timestamp)).strftime("%Y-%m-%d %H:%M:%S"))
                    all_data.append(event)

            sorted_data = sorted(all_data, key=lambda x: x.dtime.timestamp(), reverse=True)
        return sorted_data[:keep_num]
