import time

from automaps.generators.base import MapGenerator, Step


class MapGeneratorPendler(MapGenerator):
    name = "Pendler"

    def _set_steps(self):
        self.steps = [
            Step("Schritt A", self.schritt_A, 1),
            Step("Schritt B", self.schritt_B, 4),
            Step("Schritt C", self.schritt_C, 2),
        ]

    def schritt_A(self):
        time.sleep(1)
        
    def schritt_B(self):
        time.sleep(4)

    def schritt_C(self):
        time.sleep(2)
        self.save_file()
        
    def save_file(self):
        with open(self.filename, "w") as f:
            f.write(f"Ich bin eine Pendlerkarte mit Daten: {self.data}\n")
