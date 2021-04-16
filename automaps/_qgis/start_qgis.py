from qgis.core import QgsApplication

import conf_local

QgsApplication.setPrefixPath(conf_local.QGIS_INSTALLATION_PATH, True)
qgs = QgsApplication([], False)
qgs.initQgis()
