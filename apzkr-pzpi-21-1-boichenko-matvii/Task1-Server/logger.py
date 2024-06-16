import logging
import sys
from typing import Union


class CustomLogger(logging.Logger):
    def __init__(self, logger_name: str, log_level: Union[int, str] = logging.INFO):
        super(CustomLogger, self).__init__(logger_name, log_level)
        self.handlers.clear()

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(logging.Formatter(
            f"%(asctime)s %(name)s %(module)s %(funcName)s %(levelname)s %(message)s"))

        self.addHandler(stream_handler)


Logger: CustomLogger = None


def configure_logger(**kwargs):
    global Logger
    if not Logger:
        Logger = CustomLogger(**kwargs)
