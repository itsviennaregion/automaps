from typing import Iterable

from jinja2 import Template
import streamlit as st

from automaps.selector import BaseSelector, SelectorSQL


class MapType:
    def __init__(
        self,
        name: str,
        description: str,
        selectors: Iterable[BaseSelector],
        print_layout: str,
    ):
        self.name = name
        self.description = description
        self.selectors = selectors
        self.print_layout = print_layout

    @property
    def selector_values(self):
        """Show widgets (if conditions defined by Selector argument
        `depends_on_selectors` are satisfied) and return selected values."""
        selector_values = {}
        has_init_values = False
        for s in self.selectors:
            if isinstance(s, BaseSelector):
                if isinstance(s, SelectorSQL):
                    self._update_sql(s, selector_values)
                if not s.depends_on_selectors:
                    selector_values[s.label] = s.widget
                else:
                    show_widget = True
                    for sel_name, sel_value in s.depends_on_selectors.items():
                        if selector_values.get(sel_name, None) != sel_value:
                            show_widget = False
                        for s2 in self.selectors:
                            if isinstance(s2, BaseSelector):
                                if s2.label == sel_name:
                                    if sel_value == s2.no_value_selected_text:
                                        show_widget = False
                    if show_widget:
                        selector_values[s.label] = s.widget
                    else:
                        selector_values[s.label] = None
                if (
                    selector_values[s.label] == s.no_value_selected_text
                    or selector_values[s.label] == []
                ):
                    has_init_values = True
            elif isinstance(s, tuple):
                try:
                    name = s[0].__name__
                    if name == "write":
                        s[0](s[1])
                    else:
                        st.error(
                            f"'{name}' nicht unterstützt! Bitte 'st.write' "
                            "verwenden."
                        )
                except Exception as e:
                    st.error(e)
        if has_init_values:
            selector_values["has_init_values"] = True
        return selector_values

    def _update_sql(self, selector: SelectorSQL, selector_values: dict):
        template = Template(selector.sql_orig)
        sql_updated = template.render(data=selector_values)
        selector.sql = sql_updated
