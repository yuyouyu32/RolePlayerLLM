import redis
from typing import Dict, Any, List


class Redis_Base_Client():
    def __init__(self, config: Dict[str, Any]):
        """
        Description:
            Initialize the redis vector client.
        Args:
            config:
                The config of redis connection:
                    {
                        'host': 'localhost',
                        'port': 6379, 
                        'db': 0,
                        'password': None,
                        'embedding_config': embedding_config
                    }
        
        """
        self.connet_pool = redis.ConnectionPool(host=config['host'],
                                         port=config['port'],
                                         db=config['db'],
                                         password=config['password'],
                                         decode_responses=True)
        
    def _scan_keys(self, pattern: str) -> List[str]:
        """
        Description:
            Scan the keys with the pattern.
        Args:
            pattern: The pattern of the keys.
        Returns:
            The list of the keys.
        Note:
            - The `_scan_keys(pattern)` function is replace for `conn.keys(pattern)`. 
            - Using the KEYS command in large databases can affect performance. This is because it returns all matching keys at once, which can cause the Redis instance to block.
            - To solve this problem, you can use the SCAN command, which returns only a small number of elements at a time, thus avoiding blocking.
        """ 
        cursor = 0
        keys = []
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            while True:
                cursor, chunk = conn.scan(cursor, match=pattern, count=100)
                keys.extend(chunk)
                if cursor == 0:
                    break
        return keys
    
    def drop_table(self, table_name: str) -> None:
        """
        Description:
            Drop the table.
        Args:
            table_name: The name of the table.
        """
        pattern = f"{table_name}:*"
        keys_to_delete = self._scan_keys(pattern)
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            for key in keys_to_delete:
                conn.delete(key)
            conn.srem('table_names', table_name)
    
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
        
    def flushdb(self):
        """
        Description:
            Flush the database.
        """
        with redis.Redis(connection_pool=self.connet_pool) as conn:
            conn.flushdb()

    def insert(self):
        pass

    def search(self):
        pass

    def updata(self):
        pass

    def show(self):
        pass