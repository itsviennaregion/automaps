import pytest
import streamlit as st
import sqlalchemy.exc

from automaps.selector import SelectorSQL

def test_options(mock_engine):
    sel = SelectorSQL("sel", "select distinct name from cities")
    assert sel.options == ["Achau", "Traiskirchen"]
    sel = SelectorSQL(
        "sel",
        "select distinct name from cities",
        additional_values=["Himberg", "Baden"],
    )
    assert sel.options == ["Himberg", "Baden", "Achau", "Traiskirchen"]
    sel = SelectorSQL(
        "sel",
        "select distinct name from cities",
        no_value_selected_text="Choose city ...",
    )
    assert sel.options == ["Choose city ...", "Achau", "Traiskirchen"]
    sel = SelectorSQL(
        "sel",
        "select distinct name from cities",
        no_value_selected_text="Choose city ...",
        additional_values=["Himberg", "Baden"],
    )
    assert sel.options == [
        "Choose city ...",
        "Himberg",
        "Baden",
        "Achau",
        "Traiskirchen",
    ]

def test_options_flawed(mock_engine):
    sel = SelectorSQL("sel", "select name from cities where name = 'Berlin'")
    assert sel.options == []

    with pytest.raises(sqlalchemy.exc.ProgrammingError):
        sel = SelectorSQL("sel", "select name from foo where name = 'Berlin'")
        sel.options


def test_widget_st(mock_engine):
    sel = SelectorSQL("sel", "select distinct name from cities", st.selectbox)
    assert sel.widget == "Achau"
    sel = SelectorSQL(
        "sel",
        "select distinct name from cities",
        st.selectbox,
        widget_args={"index": 1},
    )
    assert sel.widget == "Traiskirchen"


def test_widget_none(mock_engine):
    sel = SelectorSQL("sel", "select distinct name from cities")
    assert sel.widget == sel.options
    sel = SelectorSQL(
        "sel",
        "select distinct name from cities where name = 'Achau'",
        extract_first_option=False,
    )
    assert sel.widget == ["Achau"]
    sel = SelectorSQL(
        "sel",
        "select distinct name from cities where name = 'Achau'",
        extract_first_option=True,
    )
    assert sel.widget == "Achau"
    sel = SelectorSQL("sel", "select distinct name from cities where name = 'Berlin'")
    assert sel.widget is None
