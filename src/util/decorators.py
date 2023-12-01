import time
from util.logging import logger

def cost_calculator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        time_elapsed = end_time - start_time
        logger.info(f"Function {func.__name__} took {time_elapsed:.4f} seconds to run.")
        
        return result

    return wrapper