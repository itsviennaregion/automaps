"""This module handles QGIS projects."""

from typing import Any

from qgis.core import QgsExpressionContextUtils, QgsProject

try:
    import automapsconf
except ModuleNotFoundError:
    pass


def get_project() -> QgsProject:
    """Loads a QGIS project from the path defined in the config file into memory.

    Returns:
        QgsProject: The desired QGIS project.

    Config Values:
        FILEPATH_QGIS_PROJECT: The path to the QGIS project file.
    """
    project = QgsProject()
    project.read(automapsconf.FILEPATH_QGIS_PROJECT)
    return project


def set_project_variable(project: QgsProject, var_name: str, var_value: Any):
    """Sets a user defined variable in a given QGIS project.

    Args:
        project (QgsProject): The QGIS project to modify.
        var_name (str): The variable name.
        var_value (Any): The variable value.
    """
    QgsExpressionContextUtils.setProjectVariable(project, var_name, var_value)
