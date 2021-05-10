from typing import Dict

import streamlit as st

from automaps.maptype import MapType
from automaps.selector import SelectorSimple, SelectorSQL


MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick": MapType(
        name="ÖV-Überblick",
        description="Hier kann man eine ÖV-Überblickskarte erstellen. "
        "Das funktioniert so: ...",
        selectors=[
            SelectorSimple(
                "Räumliche Ebene",
                ["Linie", "Gemeinde"],
                st.selectbox,
                no_value_selected_text="Räumliche Ebene auswählen ...",
            ),
            SelectorSQL(
                "Linie",
                "select distinct liniennummer from geom_mabinso_strecken",
                st.selectbox,
                no_value_selected_text="Liniennummer auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Linie"},
            ),
            SelectorSQL(
                "Gemeinde",
                "select distinct gem_name from gem",
                st.selectbox,
                no_value_selected_text="Gemeinde auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Gemeinde"},
            ),
        ],
        print_layout="test_layout",
    ),
    "Test": MapType(
        name="Test",
        description="Hier kann man alles mögliche testen. " "Das funktioniert so: ...",
        selectors=[
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Ebene", ["", "Gemeinde", "Bezirk"], st.selectbox),
            SelectorSQL(
                "Gemeinde",
                "select distinct gem_name from gem",
                st.selectbox,
                depends_on_selectors={"Ebene": "Gemeinde", "Layout": "A"},
            ),
            SelectorSQL(
                "Bezirk",
                "select distinct bez_name from bez",
                st.selectbox,
                depends_on_selectors={"Ebene": "Bezirk"},
            ),
        ],
        print_layout="test_layout",
    ),
}
