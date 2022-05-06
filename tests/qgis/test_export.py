import os

import pytest

import automapsconf

automapsconf.QGIS_INSTALLATION_PATH = "/usr"
PATH = os.path.abspath(os.path.join(os.getcwd(), "tests", "qgis", "test_project.qgz"))
automapsconf.FILEPATH_QGIS_PROJECT = PATH

from automaps._qgis.export import export_layout
from automaps._qgis.layout import get_layout_by_name
from automaps._qgis.project import get_project

from qgis.core import QgsPrintLayout


@pytest.mark.parametrize("export_format", ["pdf", "PDF", "png", "PNG", "svg", "SVG"])
def test_export_layout_valid_formats(tmp_path, export_format):
    project = get_project()
    layout = get_layout_by_name(project, "myLayout")
    path = tmp_path / f"myExport.{export_format.lower()}"
    export_layout(layout, str(path), export_format)
    assert path.exists()


@pytest.mark.parametrize("export_format", ["bmp", "tiff", "doc", "jpeg", "gif"])
def test_export_layout_invalid_formats(tmp_path, export_format):
    project = get_project()
    layout = get_layout_by_name(project, "myLayout")
    path = tmp_path / f"myExport.{export_format.lower()}"
    with pytest.raises(ValueError):
        export_layout(layout, str(path), export_format)
    assert not path.exists()
