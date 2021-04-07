import os
import time

import streamlit as st

from automaps.fileserver import download_button
from automaps.generators import MapGenerator
from automaps.maptype import MapType
from automaps.selector import SelectorSQL, SelectorSimple


BASEPATH_FILESERVER = r"D:\temp\automap"


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = [("Schritt 1", self.schritt_1), ("Schritt 2", self.schritt_2)]

    def schritt_1(self):
        time.sleep(1)

    def schritt_2(self):
        time.sleep(2)
        with open(self.filename, "w") as f:
            f.write(f"Ich bin ein ÖV-Überblick mit Daten: {self.data}\n")


class MapGeneratorPendler(MapGenerator):
    name = "Pendler"

    def _set_steps(self):
        self.steps = [("Schritt A", self.schritt_A), ("Schritt B", self.schritt_B)]

    def schritt_A(self):
        time.sleep(1)

    def schritt_B(self):
        time.sleep(2)
        with open(self.filename, "w") as f:
            f.write(f"Ich bin eine Pendlerkarte mit Daten: {self.data}\n")


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
        filename = maptype.generator(
            data=selector_values, basepath_fileserver=BASEPATH_FILESERVER
        ).generate()

        with open(filename, "rb") as f:
            s = f.read()
        download_button_str = download_button(
            s, os.path.basename(filename), f"Download {os.path.basename(filename)}"
        )
        st.markdown(download_button_str, unsafe_allow_html=True)


if __name__ == "__main__":

    start_frontend()
