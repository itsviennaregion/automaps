from typing import Dict

import streamlit as st

from automaps.maptype import MapType
from automaps.selector import SelectorSimple, SelectorSQL


MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick Gebiet": MapType(
        name="ÖV-Überblick Gebiet",
        description="Hier kann man eine ÖV-Überblickskarte erstellen. "
        "Aber derzeit nur __testweise__. Sinnvolle Ergebnisse werden nur mit der "
        "__Räumlichen Ebene 'Gemeinde'__ erzeugt.",
        selectors=[
            (st.write, "## Grundeinstellungen"),
            SelectorSimple("Fahrplanversion", ["aktueller Fahrplan"], st.selectbox),
            SelectorSimple(
                "Räumliche Ebene",
                ["Gemeinde", "Bezirk"],
                st.selectbox,
                widget_args={"help": "Hier könnte __Ihr__ Hilfetext stehen!"},
                no_value_selected_text="Räumliche Ebene auswählen ...",
            ),
            SelectorSQL(
                "Gemeinde",
                "select distinct pg from bev_gemeinden",
                st.selectbox,
                no_value_selected_text="Gemeinde auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Gemeinde"},
            ),
            SelectorSQL(
                "Bezirk",
                "select distinct pb from bev_bezirke",
                st.selectbox,
                no_value_selected_text="Bezirk auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Bezirk"},
            ),
            (st.write, "## Datenlayer"),
            SelectorSQL(
                "Linien in der Gemeinde",
                """
                select distinct lineefa
                from
                    ptlinks_ptl_polyline l,
                    bev_gemeinden g
                where
                    g.pg = '{{ data["Gemeinde"] }}'
                    and ST_Intersects(l.geom, g.geom)
                """,
                st.multiselect,
                additional_values=["ALLE"],
                depends_on_selectors={"Räumliche Ebene": "Gemeinde"},
            ),
            SelectorSQL(
                "Linien im Bezirk",
                """
                select distinct lineefa
                from
                    ptlinks_ptl_polyline l,
                    bev_bezirke b
                where
                    b.pb = '{{ data["Bezirk"] }}'
                    and ST_Intersects(l.geom, b.geom)
                """,
                st.multiselect,
                additional_values=["ALLE"],
                depends_on_selectors={"Räumliche Ebene": "Bezirk"},
            ),
            SelectorSimple(
                "Sonstige Objekte",
                ["Schulen", "Siedlungskerne"],
                st.multiselect,
                widget_args={"default": ["Schulen", "Siedlungskerne"]},
            ),
            (st.write, "## Layout"),
            SelectorSimple(
                "Kartendarstellung", ["extern", "intern", "reduziert"], st.radio
            ),
            SelectorSimple(
                "Grundkarte",
                [
                    "basemap.at Vector",
                    "basemap.at Standard",
                    "basemap.at Grau",
                    "basemap.at Stumm Grau",
                    "OpenStreetMap",
                ],
                st.radio,
            ),
            SelectorSimple("Dateiformat", ["PDF"], st.radio),
        ],
        print_layout="ÖV-Überblick Gebiet",
    ),
    "Test": MapType(
        name="Test",
        description="Hier kann man alles mögliche testen.",
        selectors=[
            SelectorSimple("Layout", ["A", "B"], st.radio),
            SelectorSimple("Ebene", ["Gemeinde", "Bezirk"], st.selectbox),
            SelectorSQL(
                "Gemeinde",
                "select distinct gem_name from gem",
                st.selectbox,
                no_value_selected_text="...???...",
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
