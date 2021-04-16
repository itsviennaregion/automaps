from qgis.core import QgsLayout, QgsLayoutExporter

import conf_local

def export_layout(layout: QgsLayout, filepath: str):
    exporter = QgsLayoutExporter(layout)
    exporter.exportToPdf(filepath, QgsLayoutExporter.PdfExportSettings())