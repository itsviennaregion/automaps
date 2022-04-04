import logging
from typing import Optional, Union
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


def shorten_uuid(uuid: Union[UUID, str], extra_short: Optional[bool] = False):
    uuid = str(uuid)
    try:
        prefix = "" if extra_short else uuid.split("-")[0]
        return prefix + uuid.split("-")[1]
    except IndexError:
        return uuid
