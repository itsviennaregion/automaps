import time

from collections import OrderedDict

from automaps.generators.base import MapGenerator, Step


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Projekt laden": Step(self.load_project, 0.5),
                "Layer filtern": Step(self.filter_layers, 1),
                "Kartenausschnitt festlegen": Step(self.set_extent, 1),
                "Karte exportieren": Step(self.export_layout, 0.5),
            }
        )

    def load_project(self):
        project = self._get_project()
        layout = self._get_print_layout(project)
        self.step_data.project = project
        self.step_data.layout = layout

    def filter_layers(self):
        time.sleep(0.5)

    def set_extent(self):
        time.sleep(0.5)

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
