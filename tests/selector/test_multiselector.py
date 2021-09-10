from automaps.selector import MultiSelector, SelectorSimple, SelectorSQL


def test_multiselector():
    sel_simple = SelectorSimple("sel_simple", [500, 530, 42])
    sel_sql = SelectorSQL("sel_sql", "select distinct name from cities")
    sel = MultiSelector("sel_multi", [sel_simple, sel_sql])
    assert len(sel.selectors) == 2
    assert sel.selectors[0].label == "sel_simple"
    assert sel.selectors[1].label == "sel_sql"
