from collections import OrderedDict
import time


from automaps.generators.base import MapGenerator, Step


class MapGeneratorTest(MapGenerator):
    name = "Test"

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
        self._set_project_variable(self.step_data.project, "data", str(self.data))

    def filter_layers(self):
        layer = self.step_data.project.mapLayersByName("gem")[0]
        layer.setSubsetString(f"gem_name = '{self.data['Gemeinde']}'")
        self._set_project_variable(
            self.step_data.project, "gemeinde_aktiv", self.data["Gemeinde"]
        )

    def set_extent(self):
        time.sleep(0.5)

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
