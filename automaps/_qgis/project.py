from typing import Any

from qgis.core import QgsExpressionContextUtils, QgsProject

import conf_local


def get_project() -> QgsProject:
    project = QgsProject()
    project.read(conf_local.FILEPATH_QGIS_PROJECT)
    return project


def set_project_variable(project: QgsProject, var_name: str, var_value: Any):
    QgsExpressionContextUtils.setProjectVariable(project, var_name, var_value)
