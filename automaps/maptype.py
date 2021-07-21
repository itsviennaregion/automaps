from typing import Any, Callable, Dict, Iterable, Tuple, Union

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
    def selector_values(self) -> Dict[str, Any]:
        """Show widgets (if conditions defined by Selector argument
        `depends_on_selectors` are satisfied) and return selected values."""
        _selector_values: Dict[str, Any] = {}
        has_init_values = False
        for element in self.ui_elements:
            if isinstance(element, BaseSelector):
                # Process Jinja template?
                if isinstance(element, SelectorSQL):
                    self._update_sql(element, _selector_values)

                # Show Selector?
                if not element.depends_on_selectors:
                    _selector_values[element.label] = element.widget
                    if element.provide_raw_options:
                        _selector_values[
                            f"{element.label} OPTIONS"
                        ] = element.options_raw
                else:
                    if self._widget_is_visible(element, _selector_values):
                        _selector_values[element.label] = element.widget
                        if element.provide_raw_options:
                            _selector_values[
                                f"{element.label} OPTIONS"
                            ] = element.options_raw
                    else:
                        _selector_values[element.label] = None

                # Does Selector have init values?
                if (
                    _selector_values[element.label] == element.no_value_selected_text
                    or _selector_values[element.label] == []
                ):
                    if not element.optional:
                        has_init_values = True
            elif isinstance(element, tuple):
                self._process_other_ui_element(element)

        if has_init_values:
            _selector_values["has_init_values"] = True

        return _selector_values

    def _widget_is_visible(self, sel: BaseSelector, selector_values: dict) -> bool:

        if isinstance(sel.depends_on_selectors, dict):
            # is visible, if at least one of the other selectors has the desired value
            is_visible = False
            for sel_name, sel_value in sel.depends_on_selectors.items():
                # Does it satisfy condition?
                if selector_values.get(sel_name, None) == sel_value:
                    is_visible = True
                # Is default value selected?
                # for sel2 in (
                #     x for x in self.ui_elements if isinstance(x, BaseSelector)
                # ):
                #     if sel2.label == sel_name:
                #         if (
                #             selector_values.get(sel_name, None)
                #             == sel2.no_value_selected_text
                #         ):
                #             is_visible = False
        elif isinstance(sel.depends_on_selectors, list):
            # is_visible, if at least one of the other selectors has a value
            is_visible = False
            for sel_name in sel.depends_on_selectors:
                for sel2 in (
                    x for x in self.ui_elements if isinstance(x, BaseSelector)
                ):
                    if sel2.label == sel_name:
                        print(
                            f"{sel.label} depends on {sel_name}: {selector_values.get(sel_name, None)}. Visible: {is_visible}"
                        )
                        if (
                            (
                                selector_values.get(sel_name, None)
                                != sel2.no_value_selected_text
                            )
                            and (selector_values.get(sel_name, None) != None)
                            and ((len(selector_values.get(sel_name, [])) > 0))
                        ):
                            is_visible = True

        return is_visible

    def _update_sql(self, selector: SelectorSQL, selector_values: dict):
        template = Template(selector.sql_orig)
        sql_updated = template.render(data=selector_values)
        selector.sql = sql_updated

    def _process_other_ui_element(self, element: Tuple[Callable, str]):
        try:
            name = element[0].__name__
            if name == "write":
                element[0](element[1])
            else:
                st.error(f"'{name}' nicht unterstützt! Bitte 'st.write' " "verwenden.")
        except Exception as e:
            st.error(e)
