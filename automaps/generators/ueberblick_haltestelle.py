from collections import OrderedDict

from automaps.generators.base import MapGenerator, Step


class MapGeneratorUeberblickHaltestelle(MapGenerator):
    name = "ÖV-Überblick Haltestelle"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Projektvariablen setzen": Step(self.set_variables, 1),
                "Layer filtern": Step(self.filter_layers, 1),
                "Kartenausschnitt festlegen": Step(self.set_extent, 1),
                "Karte exportieren": Step(self.export_layout, 5),
            }
        )

    def set_variables(self):
        pass

    def filter_layers(self):
        pass

    def set_extent(self):
        pass

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
        # self.step_data.project.write("/home/automaps/automaps_qgis/haltestelle.qgz")
