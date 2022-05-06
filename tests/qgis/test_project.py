import os

import automapsconf

automapsconf.QGIS_INSTALLATION_PATH = "/usr"
PATH = os.path.abspath(os.path.join(os.getcwd(), "tests", "qgis", "test_project.qgz"))
automapsconf.FILEPATH_QGIS_PROJECT = PATH

from automaps._qgis.project import get_project, set_project_variable

from qgis.core import QgsProject


def test_get_project():
    project = get_project()
    assert isinstance(project, QgsProject)
    assert project.homePath() == os.path.dirname(PATH)
    assert project.fileName() == PATH


def test_set_project_variable():
    project = get_project()
    assert project.customVariables() == {}
    set_project_variable(project, "myVar", "myVal")
    assert project.customVariables() == {"myVar": "myVal"}
