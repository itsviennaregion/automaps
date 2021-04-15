from typing import Dict
import streamlit as st

from automaps.generators import (
    MapGeneratorFahrgastzahlen,
    MapGeneratorUeberblick,
    MapGeneratorPendler,
)
from automaps.maptype import MapType
from automaps.selector import SelectorSQL, SelectorSimple


MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick": MapType(
        "ÖV-Überblick",
        "Hiermit kann man einen ÖV-Überblick erzeugen. Das funktioniert so: ...",
        [
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Linie", ["1", "2", "3"], st.selectbox),
        ],
        MapGeneratorUeberblick,
    ),
    "Fahrgastzahlen": MapType(
        "Fahrgastzahlen",
        "Hiermit kann man Karten für Fahrgastzahlen erstellen. Das funktioniert so: ... ",
        [
            SelectorSQL(
                "Linie",
                "select distinct liniennummer from mabinso.mabinso_strecken_2019100120191231",
                st.selectbox,
            )
        ],
        MapGeneratorFahrgastzahlen,
    ),
    "Pendler": MapType(
        "Pendler",
        "Hiermit kann man Pendlerkarten erzeugen. Das funktioniert so: ...",
        [
            SelectorSQL(
                "Gemeinde", "select distinct von_gemeinde from pendlergem", st.selectbox
            ),
            SelectorSimple("Richtung", ["Einpendler", "Auspendler"], st.radio),
        ],
        MapGeneratorPendler,
    ),
}
