from typing import Dict

from automaps.generators import MapGeneratorUeberblick
from automaps.generators.base import MapGenerator

GENERATORS: Dict[str, MapGenerator] = {"ÖV-Überblick": MapGeneratorUeberblick}

PORT = 5555
