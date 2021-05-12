from collections import OrderedDict

from automaps.generators.base import MapGenerator, Step


class MapGeneratorUeberblickGebiet(MapGenerator):
    name = "ÖV-Überblick Gebiet"

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
        self._set_project_variable("data", str(self.data))
        self._set_project_variable("gemeinde_aktiv", self.data["Gemeinde"])

    def filter_layers(self):
        if self.data["Gemeinde"]:
            self._set_map_layer_filter_expression(
                "bev_gemeinden", f"pg = '{self.data['Gemeinde']}'"
            )

        linien = self.data["Linien in der Gemeinde"] or self.data["Linien im Bezirk"]
        if "ALLE" in linien:
            self._remove_map_layer_filter_expression("Linien")
        else:
            self._set_map_layer_filter_expression("Linien", f"lineefa in {linien}")

        self._set_map_layer_visibility(self.data["Grundkarte"], True)

    def set_extent(self):
        self._zoom_map_to_layer_extent(
            "Hauptkarte", self._get_map_layer("bev_gemeinden")
        )

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
        self.step_data.project.write("/home/automaps/automaps_qgis/ueberblick.qgz")
