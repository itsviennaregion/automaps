from typing import Dict

import streamlit as st

from automaps.maptype import MapType
from automaps.selector import SelectorSimple, SelectorSQL


MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick": MapType(
        name="ÖV-Überblick",
        description="Hier kann man eine ÖV-Überblickskarte erstellen. "
        "Aber derzeit nur __testweise__. Sinnvolle Ergebnisse werden nur mit der "
        "__Räumlichen Ebene 'Gemeinde'__ erzeugt.",
        selectors=[
            (st.write, "## Grundeinstellungen"),
            SelectorSimple("Fahrplanversion", ["aktueller Fahrplan"], st.selectbox),
            SelectorSimple(
                "Räumliche Ebene",
                [
                    "Haltestelle",
                    "Linie",
                    "Ort/Stadt",
                    "Gemeinde",
                    "Bezirk",
                    "Bundesland",
                    "Ausschreibungsregion",
                ],
                st.selectbox,
                widget_args={"help": "Hier könnte __Ihr__ Hilfetext stehen!"},
                no_value_selected_text="Räumliche Ebene auswählen ...",
            ),
            (st.write, "## Datenlayer"),
            # Räumliche Ebene: Haltestelle
            SelectorSQL(
                "Haltestelle",
                "select distinct vonhstname from geom_mabinso_strecken",
                st.multiselect,
                depends_on_selectors={"Räumliche Ebene": "Haltestelle"},
            ),
            # Räumliche Ebene: Linie
            SelectorSimple(
                "Bus und/oder Bahn",
                ["Bus", "Bahn"],
                st.multiselect,
                depends_on_selectors={"Räumliche Ebene": "Linie"},
            ),
            SelectorSQL(
                "Linie Bus",
                "select distinct liniennummer from geom_mabinso_strecken "
                "where liniennummer::int < 300",
                st.selectbox,
                no_value_selected_text="Liniennummer auswählen ...",
                depends_on_selectors={"Bus und/oder Bahn": ["Bus"]},
            ),
            SelectorSQL(
                "Linie Bahn",
                "select distinct liniennummer from geom_mabinso_strecken "
                "where liniennummer::int >= 300",
                st.selectbox,
                no_value_selected_text="Liniennummer auswählen ...",
                depends_on_selectors={"Bus und/oder Bahn": ["Bahn"]},
            ),
            SelectorSQL(
                "Linie Bus/Bahn",
                "select distinct liniennummer from geom_mabinso_strecken",
                st.selectbox,
                no_value_selected_text="Liniennummer auswählen ...",
                depends_on_selectors={"Bus und/oder Bahn": ["Bus", "Bahn"]},
            ),
            SelectorSQL(
                "Linie Bus/Bahn",
                "select distinct liniennummer from geom_mabinso_strecken",
                st.selectbox,
                no_value_selected_text="Liniennummer auswählen ...",
                depends_on_selectors={"Bus und/oder Bahn": ["Bahn", "Bus"]},
            ),
            SelectorSimple(
                "Linie oder Kurs",
                ["Linie", "Kurs"],
                st.radio,
                depends_on_selectors={"Räumliche Ebene": "Linie"},
            ),
            SelectorSQL(
                "Tagesart",
                "select distinct tagesart from geom_mabinso_strecken",
                st.selectbox,
                depends_on_selectors={"Linie oder Kurs": "Kurs"},
            ),
            # Räumliche Ebene: Gemeinde
            SelectorSQL(
                "Gemeinde",
                "select distinct gem_name from gem",
                st.selectbox,
                no_value_selected_text="Gemeinde auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Gemeinde"},
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
            SelectorSimple("Ausrichtung", ["Querformat", "Hochformat"], st.radio),
            SelectorSimple("Stil", ["Corporate Design"], st.radio),
            SelectorSimple("Format", ["A4", "A0"], st.radio),
            SelectorSimple(
                "Grundkarte",
                [
                    "basemap.at Standard",
                    "basemap.at Grau",
                    "basemap.at Stumm",
                    "OpenStreetMap",
                ],
                st.radio,
            ),
        ],
        print_layout="test_layout",
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
