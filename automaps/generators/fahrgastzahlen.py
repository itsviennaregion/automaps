import time

from automaps.generators.base import MapGenerator, Step


class MapGeneratorFahrgastzahlen(MapGenerator):
    name = "Fahrgastzahlen"

    def _set_steps(self):
        self.steps = [
            Step("Schritt 1", self.schritt_n, 2),
            Step("Schritt 2", self.schritt_m, 1),
        ]

    def schritt_n(self):
        time.sleep(2)

    def schritt_m(self):
        time.sleep(1)
        with open(self.filename, "w") as f:
            f.write(f"Ich bin eine Fahrgastzahlenkarte mit Daten: {self.data}\n")
