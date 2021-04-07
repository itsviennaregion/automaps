from typing import Iterable, Type

from automaps.db import get_engine
from automaps.generators import MapGenerator
from automaps.selector import Selector


class MapType:
    def __init__(
        self, name: str, selectors: Iterable[Selector], generator: Type[MapGenerator]
    ):
        self.name = name
        self.selectors = selectors
        self.generator = generator
