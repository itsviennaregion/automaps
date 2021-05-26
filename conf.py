from typing import Dict

import streamlit as st

from automaps.maptype import MapType
from automaps.selector import SelectorSimple, SelectorSQL


MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick Gebiet": MapType(
        name="ÖV-Überblick Gebiet",
        description="Hier kann man eine ÖV-Überblickskarte erstellen. "
        "Aber derzeit nur __testweise__.",
        ui_elements=[
            (st.write, "## Grundeinstellungen"),
            SelectorSimple(
                "Räumliche Ebene",
                ["Gemeinde", "Bezirk", "Bundesland", "Ausschreibungsregion"],
                st.selectbox,
                widget_args={
                    "help": "Nach Auswahl der räumlichen Ebene kann die gewünschte Gebietseinheit (z.B. eine bestimmte Gemeinde) ausgewählt werden."
                },
                no_value_selected_text="Räumliche Ebene auswählen ...",
            ),
            SelectorSQL(
                "Gemeinde",
                "select distinct pg from bev_gemeinden",
                st.selectbox,
                widget_args={
                    "help": "Für welche Gemeinde soll eine Karte erstellt werden?"
                },
                no_value_selected_text="Gemeinde auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Gemeinde"},
            ),
            SelectorSQL(
                "Bezirk",
                "select distinct pb from bev_bezirke",
                st.selectbox,
                widget_args={
                    "help": "Für welchen Bezirk soll eine Karte erstellt werden?"
                },
                no_value_selected_text="Bezirk auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Bezirk"},
            ),
            SelectorSQL(
                "Bundesland",
                "select distinct bl from bev_bundeslaender",
                st.selectbox,
                widget_args={
                    "help": "Für welches Bundesland soll eine Karte erstellt werden?"
                },
                no_value_selected_text="Bundesland auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Bundesland"},
            ),
            SelectorSQL(
                "Ausschreibungsregion",
                "select distinct bl from au_regionen_polygon",
                st.selectbox,
                widget_args={
                    "help": "Für welche Ausschreibungsregion soll eine Karte erstellt werden?"
                },
                no_value_selected_text="Ausschreibungsregion auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Ausschreibungsregion"},
            ),
            (st.write, "## Kartenelemente"),
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
                """,  # TODO: opbranch
                st.multiselect,
                widget_args={
                    "help": "Es können entweder alle ÖV-Linien, die das gewählte Gebiet schneiden, oder einzelne Linien gewählt werden."
                },
                additional_values=["ALLE"],
                depends_on_selectors=["Gemeinde"],
                provide_raw_options=True,
                label_ui="ÖV-Linien",
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
                widget_args={
                    "help": "Es können entweder alle ÖV-Linien, die das gewählte Gebiet schneiden, oder einzelne Linien gewählt werden."
                },
                additional_values=["ALLE"],
                depends_on_selectors=["Bezirk"],
                provide_raw_options=True,
                label_ui="ÖV-Linien",
            ),
            SelectorSQL(
                "Linien im Bundesland",
                """
                select distinct lineefa
                from
                    ptlinks_ptl_polyline l,
                    bev_bundeslaender b
                where
                    b.bl = '{{ data["Bundesland"] }}'
                    and ST_Intersects(l.geom, b.geom)
                """,
                st.multiselect,
                widget_args={
                    "help": "Es können entweder alle ÖV-Linien, die das gewählte Gebiet schneiden, oder einzelne Linien gewählt werden."
                },
                additional_values=["ALLE"],
                depends_on_selectors=["Bundesland"],
                provide_raw_options=True,
                label_ui="ÖV-Linien",
            ),
            SelectorSQL(
                "Linien in Ausschreibungsregion",
                """
                select distinct lineefa
                from
                    ptlinks_ptl_polyline l,
                    au_regionen_polygon a
                where
                    a.bl = '{{ data["Ausschreibungsregion"] }}'
                    and ST_Intersects(l.geom, a.geom)
                """,
                st.multiselect,
                widget_args={
                    "help": "Es können entweder alle ÖV-Linien, die das gewählte Gebiet schneiden, oder einzelne Linien gewählt werden."
                },
                additional_values=["ALLE"],
                depends_on_selectors=["Ausschreibungsregion"],
                provide_raw_options=True,
                label_ui="ÖV-Linien",
            ),
            # SelectorSimple(
            #     "Sonstige Objekte",
            #     ["Schulen", "Siedlungskerne"],
            #     st.multiselect,
            #     widget_args={"default": ["Schulen", "Siedlungskerne"]},
            # ),
            (st.write, "## Layout"),
            SelectorSimple(
                "Kartendarstellung",
                ["extern", "intern", "reduziert"],
                st.radio,
                widget_args={
                    "help": "Die Kartendarstellung bestimmt, welche Kartenelemente (z.B. Logos, Legenden) in welcher Form angezeigt werden."
                },
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
                widget_args={
                    "help": "Hier kann die Hintergrundkarte festgelegt werden."
                },
            ),
            SelectorSimple(
                "Dateiformat",
                ["PDF", "PNG", "SVG"],
                st.radio,
                widget_args={
                    "help": "In welchem Dateiformat soll die Karte erstellt werden? _SVG_ eignet sich am besten, für weitere Nachbearbeitung."
                },
            ),
        ],
        print_layout="ÖV-Überblick Gebiet",
    ),
    "ÖV-Überblick Linie": MapType(
        name="ÖV-Überblick Linie",
        description="Die Karte '_ÖV-Überblick Linie_' stellt eine auswählbare Linie "
        "dar. Künftig wird darüber hinaus die Darstellung von Kursen möglich sein, "
        "abgrenzbar nach Tagestyp und Zeitfenster. Sollen in einer Karte mehrere "
        "Linien angezeigt werden, bitte den Kartentyp 'ÖV-Überblick Gebiet' wählen.",
        ui_elements=[
            (st.write, "## Grundeinstellungen"),
            (st.write, "Hier kann festgelegt werden, welche Linie in der Karte dargestellt werden soll."),
            SelectorSQL(
                "Betriebszweig",
                """select distinct name from betriebszweige""",
                st.selectbox,
                no_value_selected_text="ALLE Betriebszweige",
                label_ui="Nach Betriebszweig filtern (optional)"
            ),
            SelectorSQL(
                "Betriebszweig ID",
                """
                select kode
                from betriebszweige
                where name = '{{ data["Betriebszweig"] }}'""",
                widget_method=None,
                depends_on_selectors=["Betriebszweig"],
            ),
            SelectorSQL(
                "Linie",
                """
                select distinct lineefa
                from ptlinks_ptl_polyline
                {% if data["Betriebszweig ID"] %}
                where opbranch = '{{ data["Betriebszweig ID"][0] }}'
                {% endif %}
                """,
                st.selectbox,
                no_value_selected_text="Linie auswählen ...",
                # depends_on_selectors=["Betriebszweig ID"],
            ),
            # (st.write, "## Kartenelemente"),
            # SelectorSimple(
            #     "Linie oder Kurs",
            #     ["Linie", "Kurs"],
            #     st.radio,
            # ),
            # SelectorSimple(
            #     "Sonstige Objekte",
            #     ["Schulen", "Siedlungskerne"],
            #     st.multiselect,
            #     widget_args={"default": ["Schulen", "Siedlungskerne"]},
            # ),
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
            SelectorSimple("Dateiformat", ["PDF", "PNG", "SVG"], st.radio),
        ],
        print_layout="ÖV-Überblick Gebiet",
    ),
    # "Test": MapType(
    #     name="Test",
    #     description="Hier kann man alles mögliche testen.",
    #     ui_elements=[
    #         SelectorSimple("Layout", ["A", "B"], st.radio),
    #         SelectorSimple("Ebene", ["Gemeinde", "Bezirk"], st.selectbox),
    #         SelectorSQL(
    #             "Gemeinde",
    #             "select distinct gem_name from gem",
    #             st.selectbox,
    #             no_value_selected_text="...???...",
    #             depends_on_selectors={"Ebene": "Gemeinde", "Layout": "A"},
    #         ),
    #         SelectorSQL(
    #             "Bezirk",
    #             "select distinct bez_name from bez",
    #             st.selectbox,
    #             depends_on_selectors={"Ebene": "Bezirk"},
    #         ),
    #     ],
    #     print_layout="test_layout",
    # ),
}
