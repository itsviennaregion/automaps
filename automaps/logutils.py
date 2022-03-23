import logging

from automaps.confutils import get_config_value


logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    get_config_value(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

if get_config_value("LOG_PATH"):
    fh = logging.FileHandler(get_config_value("LOG_PATH"))
    fh.setLevel(get_config_value("LOG_LEVEL_SERVER", logging.DEBUG))
    fh.setFormatter(formatter)
    logger.addHandler(fh)
