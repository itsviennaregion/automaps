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
