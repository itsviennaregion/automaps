from qgis.core import QgsApplication, QgsProject

import conf_local

def get_project() -> QgsProject:
    project = QgsProject()
    project.read(conf_local.FILEPATH_QGIS_PROJECT)

    # Problem: Kein Zugriff auf Datenbank -> Layer 'gem' ist 'invalid'
    # Mögliche Lösungsansätze: Authentication Manager
    # QgsApplication, QgsAuthManager

    # print(project.mapLayers())
    # layer = list(project.mapLayers().values())[0]
    # features = layer.getFeatures()
    # for feature in features:
    #     print(feature.id())
    return project