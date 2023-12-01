from .redis_base import Redis_Base_Client
import redis
from typing import Dict, Any, List, Union, Awaitable
import json


class RedisHashClient(Redis_Base_Client):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
    
    def insert(self, table_name: str, table_key_set: List[str], init_data: List[Any], primary_key: str = None) -> Union[Awaitable, Any]:
        """
        Description:
            Insert data into Redis.
        Args:
            table_name: The name of table.
            table_key_set: The key set of table.
            init_data: The init data of table.
            primary_key: The primary key of table.
        Return:
            Returns the number of fields that were added.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            data_dict = dict(zip(table_key_set, init_data))

            serialized_data_dict = {key: json.dumps(value) if isinstance(value, (list, dict)) else value for key, value in data_dict.items()}
            if primary_key:
                data_key = f"{table_name}:{data_dict[primary_key]}"
            else:
                data_key = f"{table_name}:{init_data[0]}"
            conn.sadd('table_names', table_name)
            return conn.hset(data_key, mapping=serialized_data_dict)

    def table_exists(self, table_name: str) -> bool:
        """
        Description:
            Check if the table exists.
        Args:
            table_name: The name of the table.
        Returns:
            True if the table exists, otherwise False.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            return conn.sismember('table_names', table_name)
        
    def search(self, table_name: str, search_keys: List[str], condition_key: str, condition_val: Any) -> List[Any]:
        """
        Description:
            Search data from Redis.
        Args:
            table_name: The name of the table.
            search_keys: The search keys.
            condition_key: The condition key.[Must primary key]
            condition_val: The condition value.
        Returns:
            The result of search.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            redis_key = f'{table_name}:{condition_val}'
            data_dict = conn.hgetall(redis_key)
            search_values = [data_dict.get(key, None) for key in search_keys]
    
            return search_values
        
    def update(self, table_name: str, key: str, value: Any, condition_key: str, condition_val: Any) -> bool:
        """
        Description:
            Update data in Redis.
        Args:
            table_name: The name of the table.
            key: The key to update.
            value: The value to update.
            condition_key: The condition key.
            condition_val: The condition value.
        Returns:
            True if update successfully, otherwise False.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            redis_key = f'{table_name}:{condition_val}'
            if not conn.exists(redis_key):
                return False
            if isinstance(value, (list, dict)):
                value = json.dumps(value)

            conn.hset(redis_key, key, value)
            return True
        
    def delete(self, table_name: str, condition_key: str, condition_val: Any) -> bool:
        """
        Description:
            Delete data from Redis.
        Args:
            table_name: The name of the table.
            condition_key: The condition key.
            condition_val: The condition value.
        Returns:
            True if delete successfully, otherwise False.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            redis_key = f'{table_name}:{condition_val}'
            if not conn.exists(redis_key):
                return False
            conn.delete(redis_key)
            return True
          
    def show(self, table_name:str, max_num: int = 5):
        """
        Description:
            Show the table.
        Args:
            table_name: The name of the table.
            max_num: The max number of the results.
        Returns:
            The list of the data.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            keys = self._scan_keys(f"{table_name}:*")
            results = []
            for key in keys[:max_num]:
                results.append(conn.hgetall(key))
        return results
    
    def value_exists(self, table_name: str, column_name: str, value: Any) -> bool:
        """
        Description:
            Check if the value exists.
        Args:
            table_name: The name of the table.
            column_name: The name of the column.
            value: The value to check.
        Returns:
            True if the value exists, otherwise False.
        """
        pattern = f'{table_name}:{column_name}:{value}'
        pattern_primary = f'{table_name}:{value}'
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            return True if conn.exists(pattern_primary) or conn.exists(pattern) else False

    
def unit_test():
    config = {
        'host': 'localhost',
        'port': 6379, 
        'db': 0,
        'password': None
    }
    data = {
        "agent_id": "ag00000000000001",
        "engine_worker_id": "ue00000000000001",
        "intrinsic": {
            "mood": "happy",
            "thought": "eat",
            "plan": "search food",
            "recent_story": "..."
        },
        "extrinsic": {
            "health": "healthy",
            "location": "home",
            "behavior": "wander",
            "candidate_actions": ["run", "eat", "photo"],
            "world_weather": "sunny",
            "world_time": "11am, utc-8"
        }
    }
    client = RedisHashClient(config)
    ret = client.insert('agent', ['agent_id', 'engine_worker_id', 'intrinsic', 'extrinsic'], list(data.values()), 'agent_id')
    print("insert: ", ret)
    ret = client.search('agent', ['agent_id', 'engine_worker_id', 'intrinsic', 'extrinsic'], 'agent_id', 'ag00000000000001')
    print("search: ", ret)
    ret = client.update('agent', 'engine_worker_id', '000002', 'agent_id', 'ag00000000000001')
    print("update: ", ret)
    ret = client.show('agent', 10)
    print("show: ", ret)
    ret = client.delete('agent', 'agent_id', 'ag00000000000001')
    print("delete: ", ret)
    client.flushdb()


if __name__ == '__main__':
    unit_test()
