import time

from qgis.core import QgsApplication, QgsProject, QgsLayoutExporter
import streamlit as st

from automaps.generators.base import MapGenerator, Step
# from automaps ._qgis.qgis_init import get_project
from automaps._qgis.project import get_project
from automaps._qgis.export import export_layout

import conf
import conf_local


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = [
            Step("Schritt 1", self.schritt_1, 1),
            Step("Schritt 2", self.schritt_2, 2),
        ]

    def schritt_1(self):
        self.project = get_project()

    def schritt_2(self):
        export_layout(self.get_print_layout(), self.filename)
