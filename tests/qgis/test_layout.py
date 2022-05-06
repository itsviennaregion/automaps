import os

import automapsconf

automapsconf.QGIS_INSTALLATION_PATH = "/usr"
PATH = os.path.abspath(os.path.join(os.getcwd(), "tests", "qgis", "test_project.qgz"))
automapsconf.FILEPATH_QGIS_PROJECT = PATH

from automaps._qgis.layout import get_layout_by_name
from automaps._qgis.project import get_project

from qgis.core import QgsPrintLayout


def test_get_layout_by_name():
    project = get_project()
    layout = get_layout_by_name(project, "myLayout")
    assert isinstance(layout, QgsPrintLayout)
    assert layout.name() == "myLayout"
