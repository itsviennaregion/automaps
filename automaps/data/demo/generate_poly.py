from collections import OrderedDict

from automaps.generators.base import MapGenerator, Step


class MapGeneratorPoly(MapGenerator):
    name = "Districts in Vienna"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Initialize project": Step(self.init_project, 1),
                "Filter layers": Step(self.filter_layers, 1),
                "Zoom to extent": Step(self.set_extent, 1),
                "Export map": Step(self.export_layout, 5),
            }
        )

    def init_project(self):
        self._init_layers()
        self._set_project_variable(
            "data", self.data
        )
        self._set_map_layer_visibility("districts", True)
        self._set_map_layer_visibility("OpenStreetMap", True)

    def filter_layers(self):
        self._set_map_layer_filter_expression(
                "districts", f"NAMEK = '{self.data['District name']}'"
        )

    def set_extent(self):
        self._zoom_map_to_layer_extent(
            "Map 1", self._get_map_layer("districts")
        )

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
        self.step_data.project.write("./poly_out.qgz")
        del self.step_data.project
