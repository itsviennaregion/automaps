import time

from automaps.generators.base import MapGenerator, Step


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = [Step("Schritt 1", self.schritt_1, 1), Step("Schritt 2", self.schritt_2, 3)]

    def schritt_1(self):
        time.sleep(1)

    def schritt_2(self):
        time.sleep(3)
        with open(self.filename, "w") as f:
            f.write(f"Ich bin ein ÖV-Überblick mit Daten: {self.data}\n")
