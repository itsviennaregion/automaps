from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable

import pandas as pd
import streamlit as st

from automaps.db import get_engine


class Selector(ABC):
    label: str
    options: Iterable[Any]
    widget_method: Any
    no_value_selected_text: str
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
        no_value_selected_text: str = "",
        widget_args: dict = {},
        depends_on_selectors: Dict[str, Any] = None,
    ):
        self.label = label
        self.options = options
        self.no_value_selected_text = no_value_selected_text
        if len(no_value_selected_text) > 0:
            self.options = [no_value_selected_text] + self.options
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
        no_value_selected_text: str = "",
        widget_args: dict = {},
        depends_on_selectors: Dict[str, Any] = None,
    ):
        self.label = label
        self.sql = sql
        self.widget_method = widget_method
        self.no_value_selected_text = no_value_selected_text
        self.widget_args = widget_args
        self.depends_on_selectors = depends_on_selectors

    @property
    def options(self) -> Iterable[Any]:
        options = read_options_sql(self.sql)
        if len(self.no_value_selected_text) > 0:
            options = [self.no_value_selected_text] + options
        return options

    @property
    def widget(self):
        return self.widget_method(self.label, self.options, **self.widget_args)


@st.cache(show_spinner=False, ttl=3600)
def read_options_sql(sql) -> Iterable[Any]:
    return sorted(pd.read_sql(sql, get_engine()).iloc[:, 0])
