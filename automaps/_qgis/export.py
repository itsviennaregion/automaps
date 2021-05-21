from qgis.core import QgsLayout, QgsLayoutExporter

import conf_local


def export_layout(layout: QgsLayout, filepath: str, file_format: str):
    exporter = QgsLayoutExporter(layout)
    if file_format.lower() == "pdf":
        pdf_settings = QgsLayoutExporter.PdfExportSettings()
        pdf_settings.rasterizeWholeImage = True
        exporter.exportToPdf(filepath, pdf_settings)
    elif file_format.lower() == "png":
        # Don't show the following error message
        # ERROR 6: The PNG driver does not support update access to existing datasets.
        # https://gis.stackexchange.com/questions/360254/pyqgis-exporting-print-layout-error-6-the-png-driver-does-not-support-update
        from osgeo import gdal

        gdal.PushErrorHandler("CPLQuietErrorHandler")

        image_settings = QgsLayoutExporter.ImageExportSettings()
        image_settings.cropToContents = True
        exporter.exportToImage(filepath, image_settings)
    elif file_format.lower() == "svg":
        svg_settings = QgsLayoutExporter.SvgExportSettings()
        svg_settings.cropToContents = True
        svg_settings.forceVectorOutput = True
        svg_settings.simplifyGeometries = True
        svg_settings.exportLabelsToSeparateLayers = True
        svg_settings.exportAsLayers = True
        exporter.exportToSvg(filepath, svg_settings)
    else:
        raise ValueError(f"Unsupported export file format: {file_format}")
