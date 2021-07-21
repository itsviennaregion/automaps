from abc import ABC, abstractmethod
from collections import namedtuple
from copy import copy
import os
from typing import Any, OrderedDict

from qgis.core import QgsMapLayer, QgsPrintLayout, QgsProject

from automaps._qgis.export import export_layout
from automaps._qgis.layout import get_layout_by_name
from automaps._qgis.project import get_project, set_project_variable


Step = namedtuple("Step", "func weight")


class StepData:
    def __init__(self, message: dict):
        self.message_to_client = message


class MapGenerator(ABC):
    name: str
    steps: OrderedDict[str, Step]

    def __init__(
        self,
        data: dict,
        basepath_fileserver: str,
        print_layout: str,
        step_data: StepData,
    ):
        self.data = data
        self.basepath_fileserver = basepath_fileserver
        self.print_layout = print_layout
        self.step_data = step_data
        self.step_data.message_to_client["filename"] = self.filename
        try:
            self.step_data.project  # type: ignore
        except AttributeError:
            self.step_data.project = self._get_project()  # type: ignore
        self.step_data.layout = self._get_print_layout()  # type: ignore

        self._set_steps()
        self.total_weight: float = sum([s.weight for s in self.steps.values()])

    @property
    def filename(self) -> str:
        data = copy(self.data)
        data.pop("maptype_dict_key", None)
        data.pop("step", None)
        data.pop("print_layout", None)
        data.pop("Dateiformat", None)
        data.pop("Linienfokus", None)
        data.pop("Geometriefokus", None)
        data.pop("Haltestellenfokus", None)
        option_keys_to_pop = [x for x in data.keys() if " OPTIONS" in x]
        for key in option_keys_to_pop:
            data.pop(key, None)
        file_ext = (
            self.data["Dateiformat"].lower()
            if self.data.get("Dateiformat", None)
            else "pdf"
        )
        return os.path.join(
            self.basepath_fileserver,
            f"{self.name}_{'_'.join(str(x) for x in data.values() if x)}.{file_ext}",
        )

    @abstractmethod
    def _set_steps(self):
        pass

    def run_step(self, name: str) -> StepData:
        self.steps[name].func()
        self.step_data.message_to_client["rel_weight"] = (
            self.steps[name].weight / self.total_weight
        )
        return self.step_data

    def _get_project(self) -> QgsProject:
        return get_project()

    def _set_project_variable(self, var_name: str, var_value: Any):
        set_project_variable(self.step_data.project, var_name, var_value)  # type: ignore

    def _get_print_layout(self) -> QgsPrintLayout:
        return get_layout_by_name(self.step_data.project, self.print_layout)  # type: ignore

    def _get_map_layer(self, layer_name: str) -> QgsMapLayer:
        layers = self.step_data.project.mapLayersByName(layer_name)  # type: ignore
        assert len(layers) == 1
        return layers[0]

    def _set_map_layer_filter_expression(self, layer_name: str, filter_expr: str):
        lyr = self._get_map_layer(layer_name)
        lyr.setSubsetString(filter_expr.replace("[", "(").replace("]", ")"))

    def _remove_map_layer_filter_expression(self, layer_name: str):
        lyr = self._get_map_layer(layer_name)
        lyr.setSubsetString("")

    def _set_map_layer_visibility(self, layer_name: str, is_visible: bool):
        layer = self._get_map_layer(layer_name)
        root = self.step_data.project.layerTreeRoot()  # type: ignore
        node = root.findLayer(layer.id())
        if node:
            node.setItemVisibilityChecked(is_visible)

    def _zoom_map_to_layer_extent(
        self, map_name: str, layer: QgsMapLayer, buffer: float = 200.0
    ):
        buffered_layer_extent = layer.extent().buffered(
            buffer
        )  # NL: Unbuffered extent ends at the maps corner. Gives the map more space.
        self.step_data.layout.itemById(map_name).zoomToExtent(buffered_layer_extent)  # type: ignore

    def _export_print_layout(self, layout: QgsPrintLayout):
        return export_layout(layout, self.filename, self.data.get("Dateiformat", "pdf"))
