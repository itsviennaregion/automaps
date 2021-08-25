from typing import Dict, Type

from automaps.generators import (
    MapGeneratorUeberblickGebiet,
    MapGeneratorUeberblickHaltestelle,
    MapGeneratorUeberblickLinie,
)
from automaps.generators.base import MapGenerator

GENERATORS: Dict[str, Type[MapGenerator]] = {
    "ÖV-Überblick Gebiet": MapGeneratorUeberblickGebiet,
    "ÖV-Überblick Linie": MapGeneratorUeberblickLinie,
    "ÖV-Überblick Haltestelle": MapGeneratorUeberblickHaltestelle,
}

PORT = 5555
