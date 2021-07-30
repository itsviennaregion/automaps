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
        self._set_project_variable(
            "data", self.data
        )  # NL: Using dict variables in QGIS works only, when they're dict or transformed to json (not str). [% map_get(  @data, 'Räumliche Ebene') %] or [% map_get(  json_to_map( @data ), 'Räumliche Ebene') %]
        gebiet_aktiv = (
            self.data["Gemeinde"]
            or self.data["Bezirk"]
            or self.data["Bundesland"]
            or self.data["Ausschreibungsregion"]
        )
        self._set_project_variable("Gebiet_Bezeichnung", gebiet_aktiv)
        self._set_project_variable("Gebiet_Ebene", self.data["Räumliche Ebene"])
        self._set_project_variable("Gebiet_WKT", self.data["Geometriefokus"])

        self._set_project_variable("Linien_in_Gebiet", self.data["Linienfokus"])

        self._set_project_variable(
            "Haltestellen_in_Gebiet", self.data["Haltestellenfokus"]
        )

    def filter_layers(self):
        if self.data["Gemeinde"]:
            self._set_map_layer_filter_expression(
                "bev_gemeinden", f"pg = '{self.data['Gemeinde']}'"
            )
            self.step_data.gebiets_layer_name = "bev_gemeinden"
            self.step_data.all_options_name = "Linien in der Gemeinde OPTIONS"
        elif self.data["Bezirk"]:
            self._set_map_layer_filter_expression(
                "bev_bezirke", f"pb = '{self.data['Bezirk']}'"
            )
            self.step_data.gebiets_layer_name = "bev_bezirke"
            self.step_data.all_options_name = "Linien im Bezirk OPTIONS"
        elif self.data["Bundesland"]:
            self._set_map_layer_filter_expression(
                "bev_bundeslaender", f"bl = '{self.data['Bundesland']}'"
            )
            self.step_data.gebiets_layer_name = "bev_bundeslaender"
            self.step_data.all_options_name = "Linien im Bundesland OPTIONS"
        elif self.data["Ausschreibungsregion"]:
            self._set_map_layer_filter_expression(
                "au_regionen_polygon", f"bl = '{self.data['Ausschreibungsregion']}'"
            )
            self.step_data.gebiets_layer_name = "au_regionen_polygon"
            self.step_data.all_options_name = "Linien in Ausschreibungsregion OPTIONS"
        else:
            raise ValueError

        self._set_map_layer_visibility(self.step_data.gebiets_layer_name, True)
        linien = (
            self.data["Linien in der Gemeinde"]
            or self.data["Linien im Bezirk"]
            or self.data["Linien im Bundesland"]
            or self.data["Linien in Ausschreibungsregion"]
        )

        self._set_map_layer_filter_expression(
            "Linien", f"lineefa in ({self.data['Linienfokus']})"
        )

        self._set_map_layer_visibility(self.data["Grundkarte"], True)

        hst_filter = "stopid is not null"
        if self.data["Haltestellen"] == "Bediente Haltestellen":
            hst_filter = f"stopid in {self.data['Haltestellenfokus']}"
        elif self.data['Haltestellen'] == "Keine":
            hst_filter = "stopid = 0"
        self._set_map_layer_filter_expression(
            "Haltestellen", hst_filter
        )
        self.step_data.hst_layer_name = "Haltestellenfokus"

    def set_extent(self):
        self._zoom_map_to_layer_extent(
            "Hauptkarte", self._get_map_layer(self.step_data.gebiets_layer_name)
        )

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
        self.step_data.project.write("/home/automaps/automaps_qgis/ueberblick.qgz")
