from qgis.core import QgsLayout, QgsLayoutExporter
from PIL import Image

# import conf_local


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

        # Remove transparent margins
        # See https://docs.qgis.org/3.16/en/docs/user_manual/print_composer/create_output.html#export-as-image 
        # "When exporting with the Crop to content option, the resulting image may 
        # therefore extend beyond the paper extent."
        with Image.open(filepath) as im:
            im = im.crop(im.getbbox())
            im.save(filepath)
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
