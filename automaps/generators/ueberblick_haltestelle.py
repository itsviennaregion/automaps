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
        self._set_project_variable(
            "data", self.data
        )  # NL: Using dict variables in QGIS works only, when they're dict or transformed to json (not str). [% map_get(  @data, 'Räumliche Ebene') %] or [% map_get(  json_to_map( @data ), 'Räumliche Ebene') %]

    def filter_layers(self):
        self._set_map_layer_filter_expression(
            "Haltestellen", f"name1 in ('{self.data['Haltestellenname']}')"
        )
        self._set_map_layer_visibility("Haltestellen", True)
        self._set_map_layer_visibility("Linien", True)
        self._set_map_layer_visibility(self.data["Grundkarte"], True)

        self._set_map_layer_visibility("Schulen", self.data["Schulen"])
        self._set_map_layer_visibility("Siedlungskerne", self.data["Siedlungskerne"])

    def set_extent(self):
        self._scale_map_to_layer_extent(
            "Hauptkarte", self._get_map_layer("Haltestellen"),
            scale=1000.0
        )
        pass

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
        # self.step_data.project.write("/home/automaps/automaps_qgis/haltestelle.qgz")
