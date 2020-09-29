import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

class Logger(object):

    def __init__(self):
        self.__info_logger = self.__create_info_logger()
        self.__error_logger = self.__create_error_logger()

    def log_info(self, message):
        self.__info_logger.info(message)

    def log_warning(self, message):
        self.__info_logger.warning(message)

    def log_error(self, message):
        self.__error_logger.error(message)

    def log_critical(self, message):
        self.__error_logger.critical(message)

    def __create_info_logger(self):
        
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        if not os.path.isdir("ts3logs"):
            os.mkdir("ts3logs")

        handler = TimedRotatingFileHandler("ts3logs/logs_", when="midnight", interval=1)
        handler.suffix = "%Y%m%d.log"
        handler.setFormatter(formatter)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        logger = logging.getLogger("info_logger")
        logger.setLevel(logging.INFO)

        logger.addHandler(console_handler)
        logger.addHandler(handler)

        return logger

    def __create_error_logger(self):
        
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        if not os.path.isdir("ts3logs"):
            os.mkdir("ts3logs")

        handler = TimedRotatingFileHandler("ts3logs/errorlogs_", when="midnight", interval=1)
        handler.suffix = "%Y%m%d.log"
        handler.setFormatter(formatter)

        logger = logging.getLogger("error_logger")
        logger.setLevel(logging.ERROR)
        logger.addHandler(handler)

        return logger