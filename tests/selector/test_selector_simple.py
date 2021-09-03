import streamlit as st

from automaps.selector import SelectorSimple


def test_options():
    sel = SelectorSimple("sel", [500, 530, 42])
    assert sel.options == [500, 530, 42]
    sel = SelectorSimple(
        "sel", [500, 530, 42], no_value_selected_text="Choose your number ..."
    )
    assert sel.options == ["Choose your number ...", 500, 530, 42]
    sel = SelectorSimple("sel", [500, 530, 42], st.selectbox)
    assert sel.options == [500, 530, 42]


def test_widget_st():
    sel = SelectorSimple("sel", [500, 530, 42], st.selectbox)
    assert sel.widget == 500
    sel = SelectorSimple("sel", [500, 530, 42], st.selectbox, widget_args={"index": 1})
    assert sel.widget == 530
    sel = SelectorSimple("sel", [500, 530, 42], st.multiselect)
    assert sel.widget == []


def test_widget_none():
    sel = SelectorSimple("sel", ["a", "b", "c"])
    assert sel.widget == sel.options
    assert sel.widget == ["a", "b", "c"]
    sel = SelectorSimple("sel", [])
    assert sel.widget is None
