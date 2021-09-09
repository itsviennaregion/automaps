import streamlit as st

from automaps.maptype import MapType
from automaps.selector import MultiSelector, SelectorSimple, SelectorSQL

def test_no_streamlit_widgets(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSimple("sel_simple", [500, 530, 42]),
            SelectorSQL("sel_sql", "select distinct name from cities"),
        ],
        "my_print_layout"
    )
    assert maptype.selector_values == {
        "sel_simple": [500, 530, 42], 
        "sel_sql": ["Achau", "Traiskirchen"], 
        "selectors_to_exclude_from_filename": []
    }


def test_with_streamlit_widgets(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSimple("sel_simple", [500, 530, 42], st.selectbox),
            SelectorSQL("sel_sql", "select distinct name from cities", st.multiselect),
        ],
        "my_print_layout"
    )
    assert maptype.selector_values == {
        "sel_simple": 500, 
        "sel_sql": [], 
        "selectors_to_exclude_from_filename": [],
        "has_init_values": True
    }


def test_multiselector(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            MultiSelector("sel_multi", [
                SelectorSQL("sel_mul_sql", "select distinct name from cities", st.multiselect, {"default": ["Achau", "Traiskirchen"]}),
                SelectorSimple("sel_mul_simple", [500, 530, 42], st.selectbox, {"index": 1}),
            ])
        ],
        "my_print_layout"
    )
    assert maptype.selector_values == {
        "sel_multi": ["Achau", "Traiskirchen"],
        "selectors_to_exclude_from_filename": [],
    }


def test_dependencies(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSQL("sel_sql", "select distinct name from cities", st.multiselect),
            SelectorSimple("sel_simple", [500, 530, 42], st.selectbox, depends_on_selectors=["sel_sql"]),
        ],
        "my_print_layout"
    )
    assert maptype.selector_values == {
        "sel_sql": [], 
        "sel_simple": None, 
        "selectors_to_exclude_from_filename": [],
        "has_init_values": True
    }
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSQL("sel_sql", "select distinct name from cities", st.multiselect, {"default": "Achau"}),
            SelectorSimple("sel_simple", [500, 530, 42], st.selectbox, depends_on_selectors=["sel_sql"]),
        ],
        "my_print_layout"
    )
    assert maptype.selector_values == {
        "sel_sql": ["Achau"], 
        "sel_simple": 500, 
        "selectors_to_exclude_from_filename": []
    }
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSimple("sel_simple", [500, 530, 42], st.selectbox, depends_on_selectors=["sel_sql"]),
            SelectorSQL("sel_sql", "select distinct name from cities", st.multiselect, {"default": "Achau"}),
        ],
        "my_print_layout"
    )
    assert maptype.selector_values == {
        "sel_simple": None, 
        "sel_sql": ["Achau"], 
        "selectors_to_exclude_from_filename": []
    }
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSQL("sel_sql", "select distinct name from cities", st.multiselect, {"default": "Achau"}),
            SelectorSimple("sel_simple", [500, 530, 42], st.selectbox, depends_on_selectors={"sel_sql": ["Traiskirchen"]}),
        ],
        "my_print_layout"
    )
    assert maptype.selector_values == {
        "sel_sql": ["Achau"], 
        "sel_simple": None, 
        "selectors_to_exclude_from_filename": []
    }
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSQL("sel_sql", "select distinct name from cities", st.multiselect, {"default": "Traiskirchen"}),
            SelectorSimple("sel_simple", [500, 530, 42], st.selectbox, depends_on_selectors={"sel_sql": ["Traiskirchen"]}),
        ],
        "my_print_layout"
    )
    assert maptype.selector_values == {
        "sel_sql": ["Traiskirchen"], 
        "sel_simple": 500, 
        "selectors_to_exclude_from_filename": []
    }