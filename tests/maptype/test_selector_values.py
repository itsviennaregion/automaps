import pytest
import streamlit as st

from automaps.generators.base import MapGenerator
from automaps.maptype import MapType
from automaps.selector import MultiSelector, SelectorSimple, SelectorSQL


def test_no_streamlit_widgets(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSimple("sel_simple", [500, 530, 42]),
            SelectorSQL("sel_sql", "select distinct name from cities"),
            SelectorSimple("File Format", ["PDF"], use_for_file_format=True),
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "sel_simple": [500, 530, 42],
        "sel_sql": ["Achau", "Traiskirchen"],
        "selectors_to_exclude_from_filename": [],
        "File Format": ["PDF"],
        "!FILEFORMAT!": ["PDF"],
    }


def test_with_streamlit_widgets(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSimple("sel_simple", [500, 530, 42], st.selectbox),
            SelectorSQL("sel_sql", "select distinct name from cities", st.multiselect),
            SelectorSimple("File Format", ["PDF"], use_for_file_format=True),
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "sel_simple": 500,
        "sel_sql": [],
        "selectors_to_exclude_from_filename": [],
        "has_init_values": True,
        "File Format": ["PDF"],
        "!FILEFORMAT!": ["PDF"],
    }


def test_multiselector(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            MultiSelector(
                "sel_multi",
                [
                    SelectorSQL(
                        "sel_mul_sql",
                        "select distinct name from cities",
                        st.multiselect,
                        {"default": ["Achau", "Traiskirchen"]},
                    ),
                    SelectorSimple(
                        "sel_mul_simple", [500, 530, 42], st.selectbox, {"index": 1}
                    ),
                ],
            )
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "sel_multi": ["Achau", "Traiskirchen"],
        "selectors_to_exclude_from_filename": [],
    }


def test_multiselector_file_format(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            MultiSelector(
                "File Format",
                [
                    SelectorSimple("File Format", ["PDF"], use_for_file_format=True),
                    SelectorSimple("File Format", ["PDF"], use_for_file_format=True),
                ],
            )
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "File Format": ["PDF"],
        "!FILEFORMAT!": ["PDF"],
        "selectors_to_exclude_from_filename": [],
    }


def test_too_many_file_formats(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSimple("File Format", ["PDF"], use_for_file_format=True),
            SelectorSimple("File Format invalid", ["PDF"], use_for_file_format=True),
        ],
        "my_print_layout",
        MapGenerator,
    )
    with pytest.raises(ValueError):
        maptype.selector_values


def test_dependencies(mock_engine):
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSQL("sel_sql", "select distinct name from cities", st.multiselect),
            SelectorSimple(
                "sel_simple",
                [500, 530, 42],
                st.selectbox,
                depends_on_selectors=["sel_sql"],
            ),
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "sel_sql": [],
        "sel_simple": None,
        "selectors_to_exclude_from_filename": [],
        "has_init_values": True,
    }
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSQL(
                "sel_sql",
                "select distinct name from cities",
                st.multiselect,
                {"default": "Achau"},
            ),
            SelectorSimple(
                "sel_simple",
                [500, 530, 42],
                st.selectbox,
                depends_on_selectors=["sel_sql"],
            ),
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "sel_sql": ["Achau"],
        "sel_simple": 500,
        "selectors_to_exclude_from_filename": [],
    }
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSimple(
                "sel_simple",
                [500, 530, 42],
                st.selectbox,
                depends_on_selectors=["sel_sql"],
            ),
            SelectorSQL(
                "sel_sql",
                "select distinct name from cities",
                st.multiselect,
                {"default": "Achau"},
            ),
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "sel_simple": None,
        "sel_sql": ["Achau"],
        "selectors_to_exclude_from_filename": [],
    }
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSQL(
                "sel_sql",
                "select distinct name from cities",
                st.multiselect,
                {"default": "Achau"},
            ),
            SelectorSimple(
                "sel_simple",
                [500, 530, 42],
                st.selectbox,
                depends_on_selectors={"sel_sql": ["Traiskirchen"]},
            ),
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "sel_sql": ["Achau"],
        "sel_simple": None,
        "selectors_to_exclude_from_filename": [],
    }
    maptype = MapType(
        "maptype",
        "My Description",
        [
            SelectorSQL(
                "sel_sql",
                "select distinct name from cities",
                st.multiselect,
                {"default": "Traiskirchen"},
            ),
            SelectorSimple(
                "sel_simple",
                [500, 530, 42],
                st.selectbox,
                depends_on_selectors={"sel_sql": ["Traiskirchen"]},
            ),
        ],
        "my_print_layout",
        MapGenerator,
    )
    assert maptype.selector_values == {
        "sel_sql": ["Traiskirchen"],
        "sel_simple": 500,
        "selectors_to_exclude_from_filename": [],
    }
