from collections import OrderedDict
import os

import automapsconf
automapsconf.QGIS_INSTALLATION_PATH = "/usr"
PATH = os.path.abspath(os.path.join(os.getcwd(), "tests", "qgis", "test_project.qgz"))
automapsconf.FILEPATH_QGIS_PROJECT = PATH

from automaps.generators.base import MapGenerator, Step, StepData


DATA = {"city": "Achau", "export_format": "pdf"}
STEP_DATA = StepData({})

class MyMapGenerator(MapGenerator):
    name = "My Map Generator"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Initialize": Step(self.initialize, 1),
            }
        )

    def initialize(self):
        self._set_project_variable(
            "data", self.data
        ) 

def test_init(tmp_path):
    g = MyMapGenerator(DATA, tmp_path, "myLayout", STEP_DATA)