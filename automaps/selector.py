from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable

import pandas as pd
import streamlit as st

from automaps.db import get_engine


class Selector(ABC):
    label: str
    options: Iterable[Any]
    widget_method: Any
    widget_args: dict
    depends_on_selectors: Dict[str, Any]

    @abstractmethod
    def widget(self):
        pass


class SelectorSimple(Selector):
    def __init__(
        self,
        label: str,
        options: Iterable[Any],
        widget_method,
        widget_args: dict = {},
        depends_on_selectors: Dict[str, Any] = None,
    ):
        self.label = label
        self.options = options
        self.widget_method = widget_method
        self.widget_args = widget_args
        self.depends_on_selectors = depends_on_selectors

    @property
    def widget(self):
        return self.widget_method(self.label, self.options, **self.widget_args)


class SelectorSQL(Selector):
    def __init__(
        self,
        label: str,
        sql: str,
        widget_method,
        widget_args: dict = {},
        depends_on_selectors: Dict[str, Any] = None,
    ):
        self.label = label
        self.sql = sql
        self.widget_method = widget_method
        self.widget_args = widget_args
        self.depends_on_selectors = depends_on_selectors

    @property
    def options(self) -> Iterable[Any]:
        return read_options_sql(self.sql)

    @property
    def widget(self):
        return self.widget_method(self.label, self.options, **self.widget_args)


@st.cache(show_spinner=False, ttl=3600)
def read_options_sql(sql) -> Iterable[Any]:
    return sorted(pd.read_sql(sql, get_engine()).iloc[:, 0])
