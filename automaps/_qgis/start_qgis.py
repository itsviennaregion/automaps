"""This module initializes QGIS.

Config values:
    QGIS_INSTALLATION_PATH: The path to the qgis binary.
"""

from qgis.core import QgsApplication

import automapsconf

QgsApplication.setPrefixPath(automapsconf.QGIS_INSTALLATION_PATH, True)
qgs = QgsApplication([], False)
qgs.initQgis()
