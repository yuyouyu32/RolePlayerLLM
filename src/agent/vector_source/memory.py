import websocket
import json
from util.decorators import cost_calculator
from .base import VectorDBBase
from .document import Document


class Memory(VectorDBBase):
    def __init__(self, config):
        super().__init__(config)
        self.btype = f"{config['table_name']}_"


def unit_test():
    pass

if __name__ == "__main__":
    import time
    unit_test()
