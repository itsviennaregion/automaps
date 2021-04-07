import os
import time

import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

from automaps.db import get_engine
from automaps.generators import MapGenerator
from automaps.maptype import MapType
from automaps.selector import SelectorSQL, SelectorSimple


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = [
            ("Schritt 1", self.schritt_1),
            ("Schritt 2", self.schritt_2)
        ]

    def schritt_1(self):
        time.sleep(1)
        
    def schritt_2(self):
        time.sleep(2)
        

class MapGeneratorPendler(MapGenerator):
    name = "Pendler"

    def _set_steps(self):
        self.steps = [
            ("Schritt A", self.schritt_1),
            ("Schritt B", self.schritt_2)
        ]

    def schritt_1(self):
        time.sleep(1)
        
    def schritt_2(self):
        time.sleep(2)


MAPTYPES_AVAIL = {
    "ÖV-Überblick": MapType(
        "ÖV-Überblick",
        [
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Linie", ["1", "2", "3"], st.selectbox),
        ],
        MapGeneratorUeberblick,
    ),
    "Fahrgastzahlen": MapType(
        "Fahrgastzahlen",
        [SelectorSQL("Linie", "select distinct a from b", st.selectbox)],
        MapGeneratorUeberblick,
    ),
    "Pendler": MapType(
        "Pendler",
        [
            SelectorSimple(
                "Gemeinde", ["Traiskirchen", "Mariazell", "Pfaffstätten"], st.selectbox
            ),
            SelectorSimple("Richtung", ["Einpendler", "Auspendler"], st.radio),
        ],
        MapGeneratorPendler,
    ),
}


def start_frontend():
    maptype = MAPTYPES_AVAIL[st.sidebar.radio("Kartentyp", list(MAPTYPES_AVAIL.keys()))]
    st.write(f"# {maptype.name}")
    selector_values = {}
    for s in maptype.selectors:
        selector_values[s.label] = s.widget
    for k, v in selector_values.items():
        st.write(f"{k}: __{v}__")
    if st.button("Karte erstellen"):
        maptype.generator(data=selector_values).generate()


if __name__ == "__main__":
    start_frontend()
