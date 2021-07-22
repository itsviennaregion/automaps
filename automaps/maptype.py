from typing import Any, Callable, Dict, Iterable, Tuple, Union

from jinja2 import Template
import streamlit as st

from automaps.selector import BaseSelector, MultiSelector, SelectorSQL


# UI elements can either be Selector objects or tuples like (st.write, "## Header 1")
UIElement = Iterable[Union[MultiSelector, BaseSelector, Tuple[Callable, str]]]


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
        _selector_values: Dict[str, Any] = {"selectors_to_exclude_from_filename": []}
        for element in self.ui_elements:
            if isinstance(element, MultiSelector):
                _selector_values = self._process_multi_selector_element(
                    _selector_values, element
                )

            if isinstance(element, BaseSelector):
                _selector_values = self._process_base_selector_element(
                    _selector_values, element
                )

            elif isinstance(element, tuple):
                self._process_other_ui_element(element)

        return _selector_values

    def _widget_is_visible(self, sel: BaseSelector, selector_values: dict) -> bool:
        is_visible = False
        if isinstance(sel.depends_on_selectors, dict):
            # is visible, if at least one of the other selectors has the desired value
            for sel_name, sel_value in sel.depends_on_selectors.items():
                if selector_values.get(sel_name, None) == sel_value:
                    is_visible = True
        elif isinstance(sel.depends_on_selectors, list):
            # is_visible, if at least one of the other selectors has a value
            for sel_name in sel.depends_on_selectors:
                for sel2 in (
                    x for x in self.ui_elements if isinstance(x, BaseSelector)
                ):
                    if sel2.label == sel_name:
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

    def _process_multi_selector_element(
        self, _selector_values: Dict[str, Any], multi_sel: MultiSelector
    ) -> Dict[str, Any]:
        for base_sel in multi_sel.selectors:
            _selector_values = self._process_base_selector_element(
                _selector_values, base_sel
            )
            base_value = _selector_values.pop(base_sel.label, False)
            _selector_values[multi_sel.label] = base_value
            if base_value:
                break
        
        _selector_values = self._exclude_from_filename(
            _selector_values, multi_sel
        )
        return _selector_values

    def _process_base_selector_element(
        self, _selector_values: Dict[str, Any], element: BaseSelector
    ) -> Dict[str, Any]:
        # Process Jinja template?
        if isinstance(element, SelectorSQL):
            self._update_sql(element, _selector_values)

        # Show Selector?
        if not element.depends_on_selectors:
            _selector_values = self._get_selector_values(_selector_values, element)
        else:
            if self._widget_is_visible(element, _selector_values):
                selector_values = self._get_selector_values(_selector_values, element)
            else:
                _selector_values[element.label] = None

        # Does Selector have init values?
        if (
            _selector_values[element.label] == element.no_value_selected_text
            or _selector_values[element.label] == []
        ):
            if not element.optional:
                _selector_values["has_init_values"] = True
            
        # Exclude Selector values from filename?
        _selector_values = self._exclude_from_filename(
            _selector_values, element
        )
        
        return _selector_values

    def _get_selector_values(
        self, _selector_values: Dict[str, Any], element: BaseSelector
    ) -> Dict[str, Any]:
        _selector_values[element.label] = element.widget
        if element.provide_raw_options:
            _selector_values[f"{element.label} OPTIONS"] = element.options_raw
        return _selector_values

    def _process_other_ui_element(self, element: Tuple[Callable, str]):
        try:
            name = element[0].__name__
            if name == "write":
                element[0](element[1])
            else:
                st.error(f"'{name}' nicht unterstützt! Bitte 'st.write' " "verwenden.")
        except Exception as e:
            st.error(e)

    def _exclude_from_filename(
        self,
        _selector_values: Dict[str, Any],
        element: Union[MultiSelector, BaseSelector],
    ) -> Dict[str, Any]:
        if element.exclude_from_filename:
            _selector_values["selectors_to_exclude_from_filename"].append(element.label)
        return _selector_values
