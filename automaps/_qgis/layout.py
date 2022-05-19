"""This module handles QGIS print layouts."""

from qgis.core import QgsPrintLayout, QgsProject


def get_layout_by_name(project: QgsProject, name: str) -> QgsPrintLayout:
    """Finds a QGIS print layout by name in a given QGIS project.

    Args:
        project (QgsProject): The QGIS project.
        name (str): The name of the print layout.

    Returns:
        QgsPrintLayout: The desired print layout.
    """
    layout_manager = project.layoutManager()
    layout = layout_manager.layoutByName(name)
    return layout
