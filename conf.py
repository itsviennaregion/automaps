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
            SelectorSimple("Linie", ["1", "2", "3"], st.selectbox),
            SelectorSQL(
                "Gemeinde", "select distinct von_gemeinde from pendlergem", st.selectbox
            ),
            # SelectorSQL(
            #     "Linie",
            #     "select distinct liniennummer from mabinso.mabinso_strecken_2019100120191231",
            #     st.selectbox,
            # )
        ],
        print_layout="test_layout",
    ),
}
