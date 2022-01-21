MapType is initialized with the following arguments: 

* `name (str)`: Name of the map type. This must be used as a key in the variable `GENERATORS`. 
in `/conf_server.py` (see below). The name will be shown as main heading in the UI. It is
also used to generate the radio button values for the available map types in the sidebar.
* `description (str)`: Description of the map type. Will be displayed in the frontend.
* `ui_elements (Iterable[Union[MultiSelector, BaseSelector, Tuple[Callable, str]])`: 
Iterable of UI elements, being either `selector` objects or tuples of 
`st.write` and a string, e.g. `(st.write, "## heading")`. 
    * Selector objects are used to define the choices that are displayed in the UI. 
    are defined. The selection will be displayed at the start of processing as 
    `self.data` attribute.
    * Tuples of the type `(st.write, str)` can be used to display texts in the UI,
    e.g. to display headings or further explanations. In the future
    other streamlit methods may also be supported.
* `print_layout (Union[str, Tuple[str, Dict[str, str]])`: This will print the name of the text contained in the 
QGIS project file (see `/conf_local.py`). 
`print_layout` must take one of the following two types:
    * `str`: The name of the print layout in the associated QGIS project.
    * `tuple[str, Dict[str, str]]`: 
        * At position 0 of `tuple`: The name of the selector, from which the name of the 
        print layout is to be read
        * At position 1 of the `tuple`: A mapping between the options of the selector
        and the corresponding names of the print layout.
        * Example: `print_layout=("map layout", {"external": "public transport overview area 
        [external]", "internal": "Public transport overview area [internal]", "reduced": "Public transport overview
        area [reduced]"})`
* `html_beneath_name (str, optional)`: This String can be used, to add arbitrary html code in 
the UI, right beneath the `MapType` name heading (e.g. to add custom links to a help page).

Example:
```python
MAPTYPES_AVAIL: Dict[str, MapType] = {.
    "Public transport overview": MapType(
        name="ÖV-Überblick",
        description="This can be used to create a public transport overview."
        "It works like this: ...",
        ui_elements=[
            (st.write, "## basic settings"),
            SelectorSimple(
                "Spatial layer,
                [ "line", "municipality"],
                st.selectbox,
                widget_args={"help": "Help text"},
                no_value_selected_text="Select spatial layer ...",
            ),
            SelectorSQL(
                "municipality",
                "select distinct pg from bev_municipalities",
                st.selectbox,
                no_value_selected_text="select municipality ...",
                depends_on_selectors={"spatial_level": "municipality"},
            ),
            (st.write, "## map elements"),
            SelectorSQL(
                "lines",
                """
                select distinct line_name
                from
                    pt_links l,
                    communities g
                where
                    g.name = '{{ data["municipality"] }}'
                    and ST_Intersects(l.geom, g.geom)
                """,
                st.multiselect,
                additional_values=["ALL"],
                depends_on_selectors={"spatial_level": "municipality"},
            ),
        ],
        print_layout="test_layout",
    ),
}
```
