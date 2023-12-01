import logging

class Logger:
    def __init__(self, name, level=logging.INFO, file_name=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        if file_name:
            file_handler = logging.FileHandler(file_name)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger

logger = Logger("MyLogger", level=logging.INFO).get_logger()
#logger = Logger("MyLogger", level=logging.DEBUG).get_logger()
