from collections import OrderedDict
import time

from PyQt5.QtCore import QTimer

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
        self._set_project_variable("data", str(self.data))

    def filter_layers(self):
        layer_gem = self._get_map_layer("bev_gemeinden")
        layer_gem.setSubsetString(f"pg = '{self.data['Gemeinde']}'")
        self._set_project_variable("gemeinde_aktiv", self.data["Gemeinde"])
        self.step_data.layer_gem = layer_gem

        self._set_map_layer_visibility(self.data["Grundkarte"], True)

    def set_extent(self):
        self._zoom_map_to_layer_extent("Hauptkarte", self.step_data.layer_gem)

    def export_layout(self):
        # QTimer.singleShot(1000, lambda x: x)
        self._export_print_layout(self.step_data.layout)
        self.step_data.project.write("/home/automaps/automaps_qgis/ueberblick.qgz")
