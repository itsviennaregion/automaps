from abc import ABC, abstractmethod
from collections import namedtuple
from copy import copy
import os
from typing import Any, ForwardRef, List, OrderedDict, Union

from qgis.core import (
    QgsLayerTreeGroup,
    QgsLayerTreeLayer,
    QgsMapLayer,
    QgsPrintLayout,
    QgsProject,
)

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
    data_to_exclude_from_filename: List[str] = []

    def __init__(
        self,
        data: dict,
        basepath_fileserver: str,
        print_layout: str,
        step_data: StepData,
        default_file_format: str = "pdf",
    ):
        self.data = data
        self.basepath_fileserver = basepath_fileserver
        self.print_layout = print_layout
        self.step_data = step_data
        self.file_format = self.data.pop("!FILEFORMAT!", default_file_format).lower()
        if self.file_format not in ["pdf", "png", "svg"]:
            raise ValueError(f"Unsupported export file format: {self.file_format}")
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
        for label in data.get("selectors_to_exclude_from_filename", []):
            data.pop(label)
        data.pop("selectors_to_exclude_from_filename", None)
        data.pop("maptype_dict_key", None)
        data.pop("step", None)
        data.pop("print_layout", None)
        data.pop("!FILEFORMAT!", None)
        option_keys_to_pop = [x for x in data.keys() if " OPTIONS" in x]
        for key in option_keys_to_pop:
            data.pop(key, None)
        for key in self.data_to_exclude_from_filename:
            data.pop(key, None)
        return os.path.join(
            self.basepath_fileserver,
            f"{self.name}_{'_'.join(str(x) for x in data.values() if x)}".replace(
                " ", "_"
            )
            .replace(".", "_")
            .replace("/", "_")
            + f".{self.file_format}",
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

    def _init_layers(self):
        """Initializes all layers.

        This includes:
           * removing all filter expressions (if applicable)
           * setting all layers to invisible"""
        for lyr in self._get_all_map_layers():
            try:
                lyr.setSubsetString("")
            except AttributeError:
                pass
        for node in self.step_data.project.layerTreeRoot().children():
            if isinstance(node, QgsLayerTreeLayer):
                node.setItemVisibilityCheckedRecursive(False)

    def _set_project_variable(self, var_name: str, var_value: Any):
        set_project_variable(self.step_data.project, var_name, var_value)  # type: ignore

    def _get_print_layout(self) -> QgsPrintLayout:
        return get_layout_by_name(self.step_data.project, self.print_layout)  # type: ignore

    def _get_map_layer(self, layer_name: str) -> QgsMapLayer:
        layers = self.step_data.project.mapLayersByName(layer_name)  # type: ignore
        if len(layers) == 0:
            raise ValueError(f"Could not find layer {layer_name}.")
        elif len(layers) > 1:
            raise ValueError(
                f"Found multiple ({len(layers)}) layers with name {layer_name}."
            )
        return layers[0]

    def _get_all_map_layers(self) -> List[QgsMapLayer]:
        layers = list(self.step_data.project.mapLayers().values())  # type: ignore
        return layers

    def _set_map_layer_filter_expression(self, layer_name: str, filter_expr: str):
        lyr = self._get_map_layer(layer_name)
        filter_expr = filter_expr.replace("[", "(").replace("]", ")")
        # logging.debug(f"Filter on layer '{layer_name}': {filter_expr}")
        lyr.setSubsetString(filter_expr)

    def _remove_map_layer_filter_expression(self, layer_name: str):
        lyr = self._get_map_layer(layer_name)
        lyr.setSubsetString("")

    def _set_map_layer_visibility(
        self, layer_names: Union[str, List[str]], is_visible: bool
    ):
        if isinstance(layer_names, str):
            layer_names = [layer_names]
        for layer_name in layer_names:
            layer = self._get_map_layer(layer_name)
            root = self.step_data.project.layerTreeRoot()  # type: ignore
            node = root.findLayer(layer.id())
            if node:
                node.setItemVisibilityChecked(is_visible)

    def _set_layer_labels_visibility(self, layer_name: str, is_visible: bool):
        lyr = self._get_map_layer(layer_name)
        lyr.setLabelsEnabled(is_visible)

    def _zoom_map_to_layer_extent(
        self, map_name: str, layer: QgsMapLayer, buffer: float = 200.0
    ):
        buffered_layer_extent = layer.extent().buffered(
            buffer
        )  # NL: Unbuffered extent ends at the maps corner. Gives the map more space.
        self.step_data.layout.itemById(map_name).zoomToExtent(buffered_layer_extent)  # type: ignore

    def _scale_map_to_layer_extent(
        self,
        map_name: str,
        layer: QgsMapLayer,
        buffer: float = 200.0,
        scale: float = 1000.0,
    ):
        buffered_layer_extent = layer.extent().buffered(buffer)
        self.step_data.layout.itemById(map_name).zoomToExtent(buffered_layer_extent)  # type: ignore
        self.step_data.layout.itemById(map_name).setScale(scale)  # type: ignore

    def _export_print_layout(self, layout: QgsPrintLayout):
        return export_layout(layout, self.filename, self.file_format)
