import datetime

class Event:
    dtime_format = "%Y-%m-%d %H:%M:%S"
    def __init__(self, event_type: str,
                       source: str = None,
                       obs: str = None,
                       rsp: str = None,
                       ref: str = None,
                       dtime: datetime.datetime = None,
                       dtime_str: str = None):
        self.source = source 
        self.obs = obs
        self.rsp = rsp
        self.ref = ref
        self.dtime = dtime
        self.dtime_str = dtime_str
        self.event_type = event_type
        if not self.dtime and not self.dtime_str:
            raise("dtime required!")
        if not self.dtime:
            self.dtime = datetime.datetime.fromisoformat(dtime_str)
        if not self.dtime_str:
            self.dtime_str = self.dtime.isoformat() 


