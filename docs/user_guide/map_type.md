# The `MapType` Class

[API docs](../api/maptype.md)

## Introduction

Each map type of an autoMaps project needs to consist of:

* a `MapType` object (described here)
* a generator class (a subclass of `MapGenerator`) (see
[this](map_generator.md) section)
* one or more QGIS print layouts in an associated QGIS project file (see 
[this](qgis_project.md) section)

## Description

A `MapType` object is initialized with the following arguments:

* `name (str)`: Name of the map type. The name will be shown as main heading in the UI.
It is also used to generate the radio button values for the available map types in the
sidebar.

* `description (str)`: Description of the map type. Will be displayed in the frontend.

* `ui_elements (Iterable[Union[MultiSelector, BaseSelector, Tuple[Callable, str]])`:
Iterable of UI elements, being either `selector` objects or tuples of
`st.write` and a string, e.g. `(st.write, "## heading")`.
    * Selector objects are used to define the choices that are displayed in the UI.
    The selection will be stored in the associated `MapGenerator` object in the 
    `self.data` attribute.
    * Tuples of the type `(st.write, str)` can be used to display texts in the UI,
    e.g. to display headings or further explanations.

* `print_layout (Union[str, Tuple[str, Dict[str, str]])`: This argument connects the
`MapType` with on or more QGIS print layouts. `print_layout` must take one of the
following two types:
    * `str`: The name of the print layout in the associated QGIS project.
    * `tuple[str, Dict[str, str]]`:
        * At position 0 of `tuple`: The name of the selector, from which the name of the
        print layout is to be read.
        * At position 1 of the `tuple`: A mapping between the options of the selector
        and the corresponding names of the print layout.
        Example:

```python
    print_layout=
        (
            "map layout",  # the name of the selector, as defined in `ui_elements`
            {
                "external": "Public transport overview [external]",
                "internal": "Public transport overview [internal]",
                "reduced": "Public transport overview [reduced]"
            }
        )
```

* `map_generator (Type[MapGenerator])`: The class of the associated `MapGenerator`. This
generator receives the data dictionary from the frontend, containing all the user
selections plus additional metadata, and creates the map based on this input.

* `html_beneath_name (str, optional)`: This string can be used, to add arbitrary html
code in the UI, right beneath the `MapType` name heading (e.g. to add custom links to a
help page).

## Example

```python
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
            widget_args={"help": "Choose your district!"},
            no_value_selected_text="Choose district ...",
        ),
        SelectorSQL(
            "Stop names,
            """
            select distinct name
            from stops
            where district = '{{ data["District name"] }}'
            order by name""",
            st.multiselect,
            widget_args={"help": "Choose the stops to be displayed!"},
            depends_on_selectors=["District name"],
            no_value_selected_text="Choose stops ...",
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

MAPTYPES_AVAIL = [maptype_poly]
```
