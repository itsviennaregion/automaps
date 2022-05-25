from collections import OrderedDict
import os
from pathlib import Path
from typing import get_args

import pytest
from qgis.core import QgsLayerTreeNode, QgsMapLayer, QgsPrintLayout, QgsProject

from automaps.fileserver import get_streamlit_download_path

import automapsconf

automapsconf.QGIS_INSTALLATION_PATH = "/usr"
PATH = os.path.abspath(os.path.join(os.getcwd(), "tests", "qgis", "test_project.qgz"))
automapsconf.FILEPATH_QGIS_PROJECT = PATH

from automaps.generators.base import MapGenerator, Step, StepData


DATA = OrderedDict(
    {
        "city": "Achau",
        "!FILEFORMAT!": "pdf",
        "funny_value": 123123123123,
        "numbers": [1, 2, 3],
    }
)


class MyMapGenerator(MapGenerator):
    name = "My Map Generator"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Initialize": Step(self.initialize, 1),
                "Set variables": Step(self.set_variables, 2),
            }
        )

    def initialize(self):
        self._init_layers()

    def set_variables(self):
        self._set_project_variable("city", self.data["city"])


class MyFancyMapGenerator(MyMapGenerator):
    data_to_exclude_from_filename = ["funny_value"]


@pytest.fixture
def g(tmp_path) -> MapGenerator:
    return MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")


def test_init(tmp_path):
    g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")
    assert isinstance(g, MapGenerator)
    assert g.data == DATA
    assert g.basepath_fileserver == tmp_path
    assert g.print_layout == "myLayout"
    assert g.step_data.message_to_client["filename"] == g.filename
    assert isinstance(g.step_data.project, QgsProject)
    assert isinstance(g.step_data.layout, QgsPrintLayout)
    assert g.total_weight == 3.0
    assert g.file_format == "pdf"


def test_filename(g: MapGenerator):
    assert (
        Path(g.filename).name
        == "abc123_My_Map_Generator_Achau_123123123123_[1,_2,_3].pdf"
    )


def test_exclude_from_filename(tmp_path):
    g = MyFancyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")
    assert str(DATA["funny_value"]) not in g.filename


def test_file_format(tmp_path):
    g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")
    assert g.file_format == "pdf"
    g = MyMapGenerator(
        DATA, tmp_path, "myLayout", StepData({}), "abc123", default_file_format="svg"
    )
    assert g.file_format == "svg"
    DATA["!FILEFORMAT!"] = "pdf"
    g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")
    assert g.file_format == "pdf"
    DATA["!FILEFORMAT!"] = "png"
    g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")
    assert g.file_format == "png"
    DATA["!FILEFORMAT!"] = "PNG"
    g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")
    assert g.file_format == "png"
    with pytest.raises(ValueError):
        DATA["!FILEFORMAT!"] = "bmp"
        g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")


def test_get_project(g: MapGenerator):
    assert isinstance(g._get_project(), QgsProject)


def test_init_layers(g: MapGenerator):
    subset_strings = [lyr.subsetString() for lyr in g._get_all_map_layers()]
    visibilities = [
        node.itemVisibilityChecked()
        for node in g.step_data.project.layerTreeRoot().children()
        if isinstance(node, QgsLayerTreeNode)
    ]
    assert any(len(s) > 0 for s in subset_strings)
    assert any(v for v in visibilities)

    g.run_step("Initialize")
    subset_strings = [lyr.subsetString() for lyr in g._get_all_map_layers()]
    visibilities = [
        node.itemVisibilityChecked()
        for node in g.step_data.project.layerTreeRoot().children()
        if isinstance(node, QgsLayerTreeNode)
    ]
    assert all([s == "" for s in subset_strings])
    assert all([not v for v in visibilities])


def test_set_project_variable(g: MapGenerator):
    g.run_step("Initialize")
    assert g.step_data.project.customVariables() == {}
    g.run_step("Set variables")
    assert g.step_data.project.customVariables() == {"city": g.data["city"]}


def test_get_print_layout(g: MapGenerator):
    assert isinstance(g._get_print_layout(), QgsPrintLayout)


def test_get_map_layer(g: MapGenerator):
    with pytest.raises(ValueError, match="Could not find layer"):
        g._get_map_layer("not existing layer name")
    with pytest.raises(
        ValueError, match="Found multiple .* layers with name ambiguous name."
    ):
        g._get_map_layer("ambiguous name")
    assert isinstance(g._get_map_layer("poly"), QgsMapLayer)


def test_get_all_map_layers(g: MapGenerator):
    assert all(isinstance(x, QgsMapLayer) for x in g._get_all_map_layers())


def test_set_map_layer_filter_expression(g: MapGenerator):
    assert g._get_map_layer("poly").subsetString() != "name = 'poly2'"
    g._set_map_layer_filter_expression("poly", "name = 'poly2'")
    assert g._get_map_layer("poly").subsetString() == "name = 'poly2'"


def test_remove_map_layer_filter_expression(g: MapGenerator):
    assert g._get_map_layer("poly").subsetString() == "\"name\" = 'poly1'"
    g._remove_map_layer_filter_expression("poly")
    assert g._get_map_layer("poly").subsetString() == ""


def test_set_map_layer_visibility(g: MapGenerator):
    layer = g._get_map_layer("poly")
    root = g.step_data.project.layerTreeRoot()  # type: ignore
    node = root.findLayer(layer.id())
    assert bool(node.itemVisibilityChecked())

    g._set_map_layer_visibility("poly", False)
    assert not bool(node.itemVisibilityChecked())


def test_set_layer_labels_visibility(g: MapGenerator):
    layer = g._get_map_layer("poly")
    g._set_layer_labels_visibility("poly", True)
    assert bool(layer.labelsEnabled())
    g._set_layer_labels_visibility("poly", False)
    assert not bool(layer.labelsEnabled())


def test_set_layer_style(g: MapGenerator):
    layer = g._get_map_layer("poly")
    assert layer.styleManager().currentStyle() == "default"
    g._set_layer_style("poly", "style42")
    assert layer.styleManager().currentStyle() == "style42"


def test_zoom_map_to_layer_extent(g: MapGenerator):
    assert round(g.step_data.layout.itemById("Map 1").scale()) == 164224
    g._zoom_map_to_layer_extent("Map 1", g._get_map_layer("poly"))
    assert round(g.step_data.layout.itemById("Map 1").scale()) == 50035
    g._zoom_map_to_layer_extent("Map 1", g._get_map_layer("poly"), buffer=100)
    assert round(g.step_data.layout.itemById("Map 1").scale()) == 90244673
    g._zoom_map_to_layer_extent("Map 1", g._get_map_layer("poly"), relative_buffer=0.1)
    assert round(g.step_data.layout.itemById("Map 1").scale()) == 55038


def test_scale_map_to_layer_extent(g: MapGenerator):
    assert round(g.step_data.layout.itemById("Map 1").scale()) == 164224
    g._scale_map_to_layer_extent("Map 1", g._get_map_layer("poly"))
    assert round(g.step_data.layout.itemById("Map 1").scale()) == 1000
    g._scale_map_to_layer_extent("Map 1", g._get_map_layer("poly"), scale=2000)
    assert round(g.step_data.layout.itemById("Map 1").scale()) == 2000


@pytest.mark.parametrize("export_format", ["pdf", "PDF", "png", "PNG", "svg", "SVG"])
def test_export_print_layout(tmp_path, export_format):
    DATA["!FILEFORMAT!"] = export_format
    g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}), "abc123")
    assert not (tmp_path / Path(g.filename).name).exists()
    g._export_print_layout()
    assert (tmp_path / Path(g.filename).name).exists()
