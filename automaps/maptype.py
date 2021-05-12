from typing import Callable, Iterable, Tuple, Union

from jinja2 import Template
import streamlit as st

from automaps.selector import BaseSelector, SelectorSQL


# UI elements can either be Selector objects or tuples like (st.write, "## Header 1")
UIElement = Iterable[Union[BaseSelector, Tuple[Callable, str]]]


class MapType:
    def __init__(
        self,
        name: str,
        description: str,
        ui_elements: UIElement,
        print_layout: str,
    ):
        self.name = name
        self.description = description
        self.ui_elements = ui_elements
        self.print_layout = print_layout

    @property
    def selector_values(self):
        """Show widgets (if conditions defined by Selector argument
        `depends_on_selectors` are satisfied) and return selected values."""
        selector_values = {}
        has_init_values = False
        for el in self.ui_elements:
            if isinstance(el, BaseSelector):
                if isinstance(el, SelectorSQL):
                    self._update_sql(el, selector_values)
                if not el.depends_on_selectors:
                    selector_values[el.label] = el.widget
                else:
                    show_widget = True
                    for sel_name, sel_value in el.depends_on_selectors.items():
                        if selector_values.get(sel_name, None) != sel_value:
                            show_widget = False
                        for el2 in self.ui_elements:
                            if isinstance(el2, BaseSelector):
                                if el2.label == sel_name:
                                    if sel_value == el2.no_value_selected_text:
                                        show_widget = False
                    if show_widget:
                        selector_values[el.label] = el.widget
                    else:
                        selector_values[el.label] = None
                if (
                    selector_values[el.label] == el.no_value_selected_text
                    or selector_values[el.label] == []
                ):
                    has_init_values = True
            elif isinstance(el, tuple):
                try:
                    name = el[0].__name__
                    if name == "write":
                        el[0](el[1])
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
