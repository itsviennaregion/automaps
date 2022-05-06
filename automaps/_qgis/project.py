from typing import Any

from qgis.core import QgsExpressionContextUtils, QgsProject

try:
    import automapsconf
except ModuleNotFoundError:
    pass


def get_project() -> QgsProject:
    project = QgsProject()
    project.read(automapsconf.FILEPATH_QGIS_PROJECT)
    return project


def set_project_variable(project: QgsProject, var_name: str, var_value: Any):
    QgsExpressionContextUtils.setProjectVariable(project, var_name, var_value)
