import automapsconf

automapsconf.QGIS_INSTALLATION_PATH = "/usr"

from automaps._qgis import start_qgis

from qgis.core import QgsApplication


def test_start_qgis():
    isinstance(start_qgis.qgs, QgsApplication)
