from typing import Dict, Type

from automaps.generators import MapGeneratorTest, MapGeneratorUeberblickGebiet
from automaps.generators.base import MapGenerator

GENERATORS: Dict[str, Type[MapGenerator]] = {
    "ÖV-Überblick Gebiet": MapGeneratorUeberblickGebiet,
}

PORT = 5555
