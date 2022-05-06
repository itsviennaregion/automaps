import logging
import logging.handlers
from typing import Optional, Union
from uuid import UUID

from automaps.confutils import get_config_value


def add_file_handler(logger: logging.Logger) -> bool:
    if get_config_value("LOG_PATH"):
        format_logfile = get_config_value(
            "LOG_FORMAT", "%(asctime)s -- %(levelname)-7s -- %(name)s -- %(message)s"
        )
        formatter_logfile = logging.Formatter(format_logfile)
        fh = logging.handlers.TimedRotatingFileHandler(
            get_config_value("LOG_PATH"), when="W0"  # TODO: automapsconf.py
        )
        fh.setLevel(get_config_value("LOG_LEVEL_SERVER", logging.INFO))
        fh.setFormatter(formatter_logfile)
        logger.addHandler(fh)
        return True
    return False


def shorten_uuid(uuid: Union[UUID, str], extra_short: Optional[bool] = False) -> str:
    uuid = str(uuid)
    try:
        prefix = "" if extra_short else uuid.split("-")[0]
        return prefix + uuid.split("-")[1]
    except IndexError:
        return uuid
