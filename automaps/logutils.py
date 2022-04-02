import logging
from typing import Union
from uuid import UUID

from automaps.confutils import get_config_value

BASIC_FORMAT = "%(asctime)s -- %(levelname)-7s -- %(name)s -- %(message)s"

FORMATTER_LOGFILE = logging.Formatter(get_config_value("LOG_FORMAT", BASIC_FORMAT))


def add_file_handler(logger_):
    if get_config_value("LOG_PATH"):
        fh = logging.FileHandler(get_config_value("LOG_PATH"))
        fh.setLevel(get_config_value("LOG_LEVEL_SERVER", logging.INFO))
        fh.setFormatter(FORMATTER_LOGFILE)
        logger_.addHandler(fh)


def shorten_uuid(uuid: Union[UUID, str]):
    uuid = str(uuid)
    return uuid.split("-")[1]
