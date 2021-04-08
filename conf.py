import streamlit as st

from automaps.generators import MapGeneratorUeberblick, MapGeneratorPendler
from automaps.maptype import MapType
from automaps.selector import SelectorSQL, SelectorSimple


BASEPATH_FILESERVER = r"D:\temp\automap"

MAPTYPES_AVAIL = {
    "ÖV-Überblick": MapType(
        "ÖV-Überblick",
        "Hiermit kann man einen ÖV-Überblick erzeugen. Das funktioniert so: ...",
        [
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Linie", ["1", "2", "3"], st.selectbox),
        ],
        MapGeneratorUeberblick,
    ),
    # "Fahrgastzahlen": MapType(
    #     "Fahrgastzahlen",
    #     [SelectorSQL("Linie", "select distinct a from b", st.selectbox)],
    #     MapGeneratorUeberblick,
    # ),
    "Pendler": MapType(
        "Pendler",
        "Hiermit kann man Pendlerkarten erzeugen. Das funktioniert so: ...",
        [
            SelectorSimple(
                "Gemeinde", ["Traiskirchen", "Mariazell", "Pfaffstätten"], st.selectbox
            ),
            SelectorSimple("Richtung", ["Einpendler", "Auspendler"], st.radio),
        ],
        MapGeneratorPendler,
    ),
}
