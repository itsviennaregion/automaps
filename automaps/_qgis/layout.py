from qgis.core import QgsPrintLayout, QgsProject


def get_layout_by_name(project: QgsProject, name: str) -> QgsPrintLayout:
    layout_manager = project.layoutManager()
    layout = layout_manager.layoutByName(name)
    return layout
