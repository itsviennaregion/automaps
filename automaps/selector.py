from abc import ABC, abstractmethod
from typing import Any, Iterable

import pandas as pd

from automaps.db import get_engine


class Selector(ABC):
    label: str
    options: Iterable[Any]
    widget_method: Any
    widget_args: dict

    @abstractmethod
    def widget(self):
        pass


class SelectorSimple(Selector):
    def __init__(
        self, label: str, options: Iterable[Any], widget_method, widget_args: dict = {}
    ):
        self.label = label
        self.options = options
        self.widget_method = widget_method
        self.widget_args = widget_args

    @property
    def widget(self):
        return self.widget_method(self.label, self.options, **self.widget_args)


class SelectorSQL(Selector):
    def __init__(self, label: str, sql: str, widget_method, widget_args: dict = {}):
        self.label = label
        self.sql = sql
        self.widget_method = widget_method
        self.widget_args = widget_args
        self.engine = get_engine()

    @property
    def options(self) -> Iterable[Any]:
        return sorted(pd.read_sql(self.sql, self.engine).iloc[:, 0])

    @property
    def widget(self):
        return self.widget_method(self.label, self.options, **self.widget_args)
