from collections import OrderedDict
import os
from typing import get_args

from qgis.core import QgsPrintLayout, QgsProject

import automapsconf
automapsconf.QGIS_INSTALLATION_PATH = "/usr"
PATH = os.path.abspath(os.path.join(os.getcwd(), "tests", "qgis", "test_project.qgz"))
automapsconf.FILEPATH_QGIS_PROJECT = PATH

from automaps.generators.base import MapGenerator, Step, StepData


DATA = {"city": "Achau", "export_format": "pdf", "funny_value": 123123123123}

class MyMapGenerator(MapGenerator):
    name = "My Map Generator"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Initialize": Step(self.initialize, 1),
                "Set variables": Step(self.set_variables, 2)
            }
        )

    def initialize(self):
        pass

    def set_variables(self):
        self._set_project_variable(
            "city", self.data["city"]
        ) 

class MyFancyMapGenerator(MyMapGenerator):
    data_to_exclude_from_filename = ["funny_value"]


def test_init(tmp_path):
    g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}))
    assert isinstance(g, MapGenerator)
    assert g.data == DATA
    assert g.basepath_fileserver == tmp_path
    assert g.print_layout == "myLayout"
    assert g.step_data.message_to_client["filename"] == g.filename
    assert isinstance(g.step_data.project, QgsProject)
    assert isinstance(g.step_data.layout, QgsPrintLayout)
    assert g.total_weight == 3.0


def test_exclude_from_filename(tmp_path):
    g = MyFancyMapGenerator(DATA, tmp_path, "myLayout", StepData({}))
    assert str(g.data["funny_value"]) not in g.filename


def test_run_step(tmp_path):
    g = MyMapGenerator(DATA, tmp_path, "myLayout", StepData({}))
    g.run_step("Initialize")
    assert g.step_data.project.customVariables() == {}
    g.run_step("Set variables")
    assert g.step_data.project.customVariables() == {"city": g.data["city"]}

