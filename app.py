import os
import time

import pandas as pd
from sqlalchemy import create_engine
import streamlit as st

from automaps.db import get_engine
from automaps.generators import MapGenerator
from automaps.maptype import MapType
from automaps.selector import SelectorSQL, SelectorSimple


class MapGeneratorPendler(MapGenerator):
    name = "Gen Pendler"

    def _run_qgis(self):
        time.sleep(2)


MAPTYPES_AVAIL = {
    "ÖV-Überblick": MapType(
        "ÖV-Überblick",
        [
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Linie", ["1", "2", "3"], st.selectbox),
        ],
        MapGeneratorPendler(),
    ),
    "Fahrgastzahlen": MapType(
        "Fahrgastzahlen",
        [SelectorSQL("Linie", "select distinct a from b", st.selectbox)],
        MapGeneratorPendler(),
    ),
    "Pendler": MapType(
        "Pendler",
        [
            SelectorSimple(
                "Gemeinde", ["Traiskirchen", "Mariazell", "Pfaffstätten"], st.selectbox
            ),
            SelectorSimple("Richtung", ["Einpendler", "Auspendler"], st.radio),
        ],
        MapGeneratorPendler(),
    ),
}


def start_frontend():
    maptype = MAPTYPES_AVAIL[st.sidebar.radio("Kartentyp", list(MAPTYPES_AVAIL.keys()))]
    st.write(maptype.name)
    selector_values = {}
    for s in maptype.selectors:
        selector_values[s.label] = s.widget
    for k, v in selector_values.items():
        st.write(f"{k}: {v}")
    if st.button("Karte erstellen"):
        maptype.generator.generate()


if __name__ == "__main__":
    start_frontend()
