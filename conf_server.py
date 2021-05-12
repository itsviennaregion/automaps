from typing import Dict

from automaps.generators import MapGeneratorTest, MapGeneratorUeberblickGebiet
from automaps.generators.base import MapGenerator

GENERATORS: Dict[str, MapGenerator] = {
    "Test": MapGeneratorTest,
    "ÖV-Überblick Gebiet": MapGeneratorUeberblickGebiet,
}

PORT = 5555
