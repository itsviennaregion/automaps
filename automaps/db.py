from configparser import ConfigParser
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db.ini")


def load_config(config_path: str) -> ConfigParser:
    conf = ConfigParser()
    conf.read(config_path)
    return conf


def get_engine() -> Engine:
    return create_engine(URL(**dict(load_config(CONFIG_PATH)["db"])))
