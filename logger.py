import logging
import os
from crux_automation import config
from crux_automation import crux_path
from logging.handlers import RotatingFileHandler
import logging
import sys


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class logger(metaclass=Singleton):
    def __init__(self):
        self.log = logging.getLogger()
        log_file = os.path.join(crux_path, config.get("PROJECT", "log_file"))
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler = RotatingFileHandler(log_file, maxBytes=int(config.get("PROJECT", "log_file_size")), backupCount=5)
        self.handler.setFormatter(formatter)
        self.log.addHandler(self.handler)
        sh = logging.StreamHandler(sys.stdout)
        sh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('<BR>%(asctime)s - %(levelname)s - %(message)s')
        sh.setFormatter(formatter)
        self.log.addHandler(sh)
