from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Union

import pandas as pd
import streamlit as st

from automaps.db import get_engine


class BaseSelector(ABC):
    label: str
    options: Optional[Iterable[Any]]
    widget_method: Any
    no_value_selected_text: Optional[str]
    widget_args: Optional[Dict[str, Any]]
    depends_on_selectors: Union[List[str], Dict[str, Any]]

    @abstractmethod
    def widget(self):
        pass


class SelectorSimple(BaseSelector):
    def __init__(
        self,
        label: str,
        options: Iterable[Any],
        widget_method,
        widget_args: dict = {},
        no_value_selected_text: str = "",
        depends_on_selectors: Union[List[str], Dict[str, Any]] = {},
    ):
        self.label = label
        self.options = list(options)
        self.no_value_selected_text = no_value_selected_text
        if len(no_value_selected_text) > 0:
            self.options = [no_value_selected_text] + self.options
        self.widget_method = widget_method
        self.widget_args = widget_args
        self.depends_on_selectors = depends_on_selectors

    @property
    def widget(self):
        return self.widget_method(self.label, self.options, **self.widget_args)


class SelectorSQL(BaseSelector):
    def __init__(
        self,
        label: str,
        sql: str,
        widget_method,
        widget_args: dict = {},
        no_value_selected_text: str = "",
        additional_values: Iterable[Any] = [],
        depends_on_selectors: Union[List[str], Dict[str, Any]] = {},
    ):
        self.label = label
        self.sql = sql
        self.sql_orig = sql
        self.widget_method = widget_method
        self.no_value_selected_text: str = no_value_selected_text
        self.additional_values = list(additional_values)
        self.widget_args = widget_args
        self.depends_on_selectors = depends_on_selectors

    @property
    def options(self) -> Iterable[Any]:  # type: ignore
        options = read_options_sql(self.sql)
        if len(self.additional_values) > 0:
            options = list(self.additional_values) + options
        if len(self.no_value_selected_text) > 0:
            options = [self.no_value_selected_text] + options
        return options

    @property
    def widget(self):
        if self.widget_method:
            return self.widget_method(self.label, self.options, **self.widget_args)
        else:
            if len(self.options) == 0:
                return None
            else:
                return self.options


@st.cache(show_spinner=False, ttl=3600)
def read_options_sql(sql) -> Iterable[Any]:
    return sorted(pd.read_sql(sql, get_engine()).iloc[:, 0])
