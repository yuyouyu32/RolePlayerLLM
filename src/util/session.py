import uuid
import os

class Session():
    session_file = '/mnt_data/sessions.txt'

    def __init__(self, user_id: str = "testid123", prototype_id: str = "kuma", pair_id: str = "testid123_kuma", agent_id: str = "testid123_kuma", user_name: str = "jeriffly"):
        self.user_id = user_id
        self.user_name = user_name
        self.prototype_id = prototype_id
        self.agent_id = agent_id
        self.pair_id = pair_id
