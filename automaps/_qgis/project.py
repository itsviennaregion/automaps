from qgis.core import QgsProject

import conf_local


def get_project() -> QgsProject:
    project = QgsProject()
    project.read(conf_local.FILEPATH_QGIS_PROJECT)
    return project
