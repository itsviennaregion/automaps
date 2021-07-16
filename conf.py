from typing import Dict

import streamlit as st

from automaps.maptype import MapType
from automaps.selector import SelectorSimple, SelectorSQL


MAPTYPES_AVAIL: Dict[str, MapType] = {
    "ÖV-Überblick Gebiet": MapType(
        name="ÖV-Überblick Gebiet",
        description="Die Karte '_ÖV-Überblick Gebiet_' stellt eine auswählbare "
        "Gebietseinheit (Gemeinde, Bezirk, Bundesland oder Ausschreibungsregion) dar.",
        ui_elements=[
            (st.write, "## Grundeinstellungen"),
            (
                st.write,
                "Hier kann festgelegt werden, welche Gebietseinheit dargestellt "
                "werden soll.",
            ),
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
                """
                select distinct pg 
                from bev_gemeinden
                where bl in ('Wien', 'Niederösterreich', 'Burgenland', 'Oberösterreich', 'Steiermark')""",
                st.selectbox,
                widget_args={
                    "help": "Für welche Gemeinde soll eine Karte erstellt werden?"
                },
                no_value_selected_text="Gemeinde auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Gemeinde"},
            ),
            SelectorSQL(
                "Bezirk",
                """
                select distinct pb 
                from bev_bezirke
                where bl in ('Wien', 'Niederösterreich', 'Burgenland', 'Oberösterreich', 'Steiermark')""",
                st.selectbox,
                widget_args={
                    "help": "Für welchen Bezirk soll eine Karte erstellt werden?"
                },
                no_value_selected_text="Bezirk auswählen ...",
                depends_on_selectors={"Räumliche Ebene": "Bezirk"},
            ),
            SelectorSQL(
                "Bundesland",
                """
                select distinct bl 
                from bev_bundeslaender
                where bl in ('Wien', 'Niederösterreich', 'Burgenland', 'Oberösterreich', 'Steiermark')""",
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
            (st.write, "### Sonstige Objekte"),
            SelectorSimple("Schulen", [], st.checkbox),
            SelectorSimple("Siedlungskerne", [], st.checkbox),
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
                    "basemap.at",
                    "Luftbild",
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
            SelectorSQL(
                "Linienfokus",
                """
                select unnest(ltwo.res) from (
                    select
                        case when 'ALLE' = ANY(lone.sel) then lone.opt else lone.sel end as res
                    from(
                        select
                            string_to_array(sel, ', ') sel,
                            string_to_array(opt, ', ') opt
                        from ( values
                            (
                                '{{ data["Linien in der Gemeinde"]|list|join(", ") if data["Linien in der Gemeinde"] }}',
                                '{{ data["Linien in der Gemeinde OPTIONS"]|list|join(", ") }}'
                            ),
                            (
                                '{{ data["Linien im Bezirk"]|list|join(", ") if data["Linien im Bezirk"] }}',
                                '{{ data["Linien im Bezirk OPTIONS"]|list|join(", ") }}'
                            ),
                            (
                                '{{ data["Linien im Bundesland"]|list|join(", ") if data["Linien im Bundesland"] }}',
                                '{{ data["Linien im Bundesland OPTIONS"]|list|join(", ") }}'
                            ),
                            (
                                '{{ data["Linien in Ausschreibungsregion"]|list|join(", ") if data["Linien in Ausschreibungsregion"] }}',
                                '{{ data["Linien in Ausschreibungsregion OPTIONS"]|list|join(", ") }}'
                            )
                        ) as t (sel, opt)
                    ) lone
                    where
                        array_ndims(lone.opt) > 0
                ) ltwo""",
                None,
                provide_raw_options=False,
            ),
            SelectorSQL(
                "Geometriefokus",
                """
                select
                    st_astext(geo)
                from ( values
                    ((select geom from bev_gemeinden where pg = '{{ data["Gemeinde"] if data["Linien in der Gemeinde"] }}')),
                    ((select geom from bev_bezirke where pb = '{{ data["Bezirk"] if data["Linien im Bezirk"] }}')),
                    ((select geom from bev_bundeslaender where bl = '{{ data["Bundesland"] if data["Linien im Bundesland"] }}')),
                    ((select geom from au_regionen_polygon where bl = '{{ data["Ausschreibungsregion"] if data["Linien in Ausschreibungsregion"] }}'))
                ) as t (geo)
                where
                    geo is not null""",
                None,
                provide_raw_options=False,
            ),
            SelectorSQL(
                "Haltestellenfokus",
                """
                select distinct
                    hst_id, max(geom), array_agg(lin_id)
                from (
                select
                    fromstopid hst_id,
                    lineefa lin_id,
                    st_startpoint(geom) geom
                from ptlinks_ptl_polyline
                union
                select
                    tostopid hst_id,
                    lineefa lin_id,
                    st_endpoint(geom) geom
                from ptlinks_ptl_polyline
                ) unioned
                where
                    lin_id in ({{ "'" + "', '".join(data["Linienfokus"]) + "'" if data["Linienfokus"] }})
                    and
                    st_intersects(geom, st_geomfromtext('{{ data["Geometriefokus"][0] if data["Geometriefokus"] }}', 32633))
                group by
                    hst_id""",
                None,
                depends_on_selectors=["Geometriefokus"],
                provide_raw_options=False,
            ),
        ],
        #print_layout="ÖV-Überblick Gebiet",
        print_layout="a3q_vor",
    ),
    "ÖV-Überblick Linie": MapType(
        name="ÖV-Überblick Linie",
        description="Die Karte '_ÖV-Überblick Linie_' stellt eine auswählbare Linie "
        "dar. Künftig wird darüber hinaus die Darstellung von Kursen möglich sein, "
        "abgrenzbar nach Tagestyp und Zeitfenster. Sollen in einer Karte mehrere "
        "Linien angezeigt werden, bitte den Kartentyp 'ÖV-Überblick Gebiet' wählen.",
        ui_elements=[
            (st.write, "## Grundeinstellungen"),
            (
                st.write,
                "Hier kann festgelegt werden, welche Linie in der Karte dargestellt werden soll.",
            ),
            SelectorSQL(
                "Betriebszweig",
                """select distinct name from betriebszweige""",
                st.selectbox,
                additional_values=["ALLE Betriebszweige"],
                label_ui="Nach Betriebszweig filtern (optional)",
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
            (st.write, "## Kartenelemente"),
            # SelectorSimple(
            #     "Linie oder Kurs",
            #     ["Linie", "Kurs"],
            #     st.radio,
            # ),
            (st.write, "### Sonstige Objekte"),
            SelectorSimple("Schulen", [], st.checkbox),
            SelectorSimple("Siedlungskerne", [], st.checkbox),
            (st.write, "## Layout"),
            SelectorSimple(
                "Kartendarstellung", ["extern", "intern", "reduziert"], st.radio
            ),
            SelectorSimple(
                "Grundkarte",
                [
                    "basemap.at",
                    "Luftbild",
                    "OpenStreetMap",
                ],
                st.radio,
            ),
            SelectorSimple("Dateiformat", ["PDF", "PNG", "SVG"], st.radio),
        ],
        print_layout="ÖV-Überblick Gebiet",
    ),
    "ÖV-Überblick Haltestelle": MapType(
        name="ÖV-Überblick Haltestelle",
        description="Die Karte '_ÖV-Überblick Haltestelle_' stellt eine auswählbare "
        "Haltestelle und ihre unmittelbare Umgebung dar. "
        "Künfig wird darüber hinaus die Darstellung einzelner Steige möglich sein.",
        ui_elements=[
            (st.write, "## Grundeinstellungen"),
            (
                st.write,
                "Hier kann festgelegt werden, welche Haltestelle in der Karte dargestellt werden soll.",
            ),
            # SelectorSimple(
            #     "Auswahlmethode",
            #     ["nach Haltestellenname"],
            #     st.radio,
            #     label_ui="Wie soll die Haltestelle ausgewählt werden?"
            # ),
            # SelectorSQL(
            #     "Bezirk",
            #     "select distinct pb from bev_bezirke",
            #     st.selectbox,
            #     widget_args={
            #         "help": "In welchem Bezirk soll die Haltestelle liegen?"
            #     },
            #     no_value_selected_text="Bezirk auswählen (optional)",
            #     label_ui="nach Bezirk Filtern (optional, funktioniert noch nicht)"
            # ),
            SelectorSQL(
                "Linie",
                "select distinct pubdivalinnam from stops_ptlinks",
                st.selectbox,
                widget_args={"help": "An welcher Linie soll die Haltestelle liegen?"},
                no_value_selected_text="Linie auswählen (optional) ...",
                label_ui="nach Linien Filtern (optional)",
                optional=True,
            ),
            SelectorSQL(
                "Bezirk ID",
                """select id from bev_bezirke where pb = '{{ data["Bezirk"] }}'""",
                None,
                depends_on_selectors=["Bezirk"],
            ),
            SelectorSQL(
                "Haltestellenname",
                """
                select distinct haltestelle_name 
                from stops_ptlinks
                {% if data["Linie"] != "Linie auswählen (optional) ..." %}
                where pubdivalinnam = '{{ data["Linie"] }}'
                {% endif %}
                order by haltestelle_name""",
                st.selectbox,
                no_value_selected_text="Haltestelle auswählen ...",
            ),
            (st.write, "## Kartenelemente"),
            SelectorSQL(
                "Linien an Haltestelle",
                """
                select pubdivalinnam 
                from stops_ptlinks
                where haltestelle_name = '{{ data["Haltestellenname"] }}'""",
                st.multiselect,
                depends_on_selectors=["Haltestellenname"],
                additional_values=["ALLE"],
                widget_args={"default": ["ALLE"]},
            ),
            (st.write, "### Sonstige Objekte"),
            SelectorSimple(
                "Andere Haltestellen",
                [],
                st.checkbox,
                label_ui="Andere Haltestellen",
            ),
            SelectorSimple("Schulen", [], st.checkbox),
            SelectorSimple("Siedlungskerne", [], st.checkbox),
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
        print_layout="ÖV-Überblick Haltestelle",
    )
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
