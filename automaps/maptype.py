from typing import Iterable

from automaps.selector import Selector


class MapType:
    def __init__(
        self,
        name: str,
        description: str,
        selectors: Iterable[Selector],
        print_layout: str,
    ):
        self.name = name
        self.description = description
        self.selectors = selectors
        self.print_layout = print_layout

    @property
    def selector_values(self):
        """Show widgets (if conditions are satisfied) and return selected values.
        """
        selector_values = {}
        for s in self.selectors:
            if not s.depends_on_selectors:
                selector_values[s.label] = s.widget
            else:
                show_widget = True
                for sel_name, sel_value in s.depends_on_selectors.items():
                    if selector_values.get(sel_name, None) != sel_value:
                        show_widget = False
                if show_widget:
                    selector_values[s.label] = s.widget
                else:
                    selector_values[s.label] = None
        return selector_values
