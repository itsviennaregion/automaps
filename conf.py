from typing import Dict

import streamlit as st

from automaps.maptype import MapType
from automaps.selector import SelectorSimple, SelectorSQL


MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick": MapType(
        name="ÖV-Überblick",
        description="Hiermit kann man einen ÖV-Überblick erzeugen. "
        "Das funktioniert so: ...",
        selectors=[
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Ebene", ["", "Gemeinde", "Bezirk"], st.selectbox),
            SelectorSQL(
                "Gemeinde",
                "select distinct gem_name from gem",
                st.selectbox,
                depends_on_selectors={"Ebene": "Gemeinde", "Layout": "A"}
            ),
            SelectorSQL(
                "Bezirk",
                "select distinct bez_name from bez",
                st.selectbox,
                depends_on_selectors={"Ebene": "Bezirk"}
            ),
        ],
        print_layout="test_layout",
    ),
}
