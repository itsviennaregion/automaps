from configparser import ConfigParser
import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL
import streamlit as st

try:
    import automapsconf
except ModuleNotFoundError:
    pass

# CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db.ini")


# def load_config(config_path: str) -> ConfigParser:
#     conf = ConfigParser()
#     conf.read(config_path)
#     return conf


@st.cache(allow_output_mutation=True)
def get_engine() -> Engine:
    return create_engine(URL(**automapsconf.db))
