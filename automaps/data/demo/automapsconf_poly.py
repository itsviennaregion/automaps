import streamlit as st

from automaps.maptype import MapType
from automaps.selector import SelectorSimple, SelectorSQL
from generate_poly import MapGeneratorPoly

maptype_poly = MapType(
    name="Districts in Vienna",
    description="Choose a district and get your map!",
    ui_elements=[
        SelectorSQL(
            "District name",
            """
            select distinct NAMEK
            from districtborder
            order by NAMEK""",
            st.selectbox,
            widget_args={
                "help": "Choose your district!"
            },
            no_value_selected_text="Choose district ...",
        ),
        
        SelectorSimple(
            "File Format",
            ["PDF", "PNG", "SVG"],
            st.radio,
            exclude_from_filename=True,
            use_for_file_format=True,
        ),
    ],
    print_layout="poly",
    map_generator=MapGeneratorPoly,
)
