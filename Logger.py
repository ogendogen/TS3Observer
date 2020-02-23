import logging
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

        handler = TimedRotatingFileHandler("logs.log", when="midnight", interval=1)
        handler.suffix = "%Y%m%d"
        handler.setFormatter(formatter)

        logger = logging.getLogger("info_logger")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger

    def __create_error_logger(self):
        
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

        handler = TimedRotatingFileHandler("errorlogs.log", when="midnight", interval=1)
        handler.suffix = "%Y%m%d"
        handler.setFormatter(formatter)

        logger = logging.getLogger("info_logger")
        logger.setLevel(logging.ERROR)
        logger.addHandler(handler)

        return logger