from typing import Dict

from automaps.generators import MapGeneratorTest, MapGeneratorUeberblick
from automaps.generators.base import MapGenerator

GENERATORS: Dict[str, MapGenerator] = {
    "Test": MapGeneratorTest,
    "ÖV-Überblick": MapGeneratorUeberblick,
}

PORT = 5555
