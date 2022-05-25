# User Interface Elements

[API docs](../api/selector.md)

The configuration of the selection options displayed in the UI is done with the help of
`Selector` objects.

## `BaseSelector` classes

Two selector classes derived from `selector.BaseSelector` are available:

* `SelectorSimple`: For lists of choices (e.g. "bus" or "train"), which are defined
directly in `automapsconf.py`.

* `SelectorSQL`: For lists of selections that are formed based on a database query.

These `Selector` classes share the following parameters for initialization:

* `label (str)`: name of the selector. Displayed in the UI. Furthermore
the label can be used to define dependencies between the selectors of a `MapType`
(see `depends_on_selectors` parameter).

* `widget_method (Callable, optional)`: One of the widgets provided by streamlit
(e.g. `st.radio` or `st.selectbox`). If no argument or `None` is passed, no widget for
selecting values will be displayed. The list of options created in the background (e.g.
by an SQL query) will still be available and can be edited via the `self.data` attribute
of the associated `MapGenerator`. This mechanism can be used to execute SQL queries in the
background, the results of which are not visible and selectable in the UI, but can be
used by subsequent selectors, or the associated `MapGenerator`.

* `widget_args (dict, optional)`: dictionary of arguments passed to initialize the
widget object (e.g. `{"help"="help text"}`).

* `no_value_selected_text (str, optional)`: selection option to be displayed, before a
value has been selected (e.g. "Select spatial layer ...").

* `depends_on_selectors (Union[List[str], Dict[str, Any]], optional)`: This can be used
to define conditions that must be met for the widget to be executed and displayed. It
allows to define dependencies between selectors. Either a list or a dictionary can be
passed:

    * __Dictionary__:
    Keys: labels of selectors also defined for the same `MapType`. Values: the option
    values that must be selected for the corresponding selector. If e.g. the value
    "line" must be selected for the selector with the label "Spatial layer", then
    `depends_on_selectors={"Spatial layer": "Line"}` must be set. Currently, only checks
    for equality can be performed (e.g. no greater than or unequal). If the dictionary
    contains more than one key/value pair, only one of the conditions must be met (OR
    operation).

    * __List__:
    A list of selector labels of selectors of the same `MapType`. If the corresponding
    selectors contain either `None` or the default text (`no_value_selected_text`) as
    value, the widget will not be displayed.
    For example, a selector for public transport lines can only be displayed, if a
    municipality has been selected first (`depends_on_selectors=["municipality"]`).
    If the list contains multiple selector labels, the widget will be displayed as soon
    as one of the listed listed selectors has a value selected (OR operation).

* `label_ui (str, optional)`: Alternative label of the widget to be displayed in the UI.

* `optional (bool, optional, default False)`: Indicates whether the widget is optional,
i.e. whether map generation can be started even though the widget has the default value
of (`no_value_selected_text`) or an empty list as result. Has influence on setting the
`has init values` flag in the associated `MapType`.

* `exclude_from_filename (bool, optional, default False)`: If `True` then the value(s)
of the selector will not be used to generate the filename.

The `SelectorSimple` class is also initialized with the following parameter:

* `options (Iterable[Any])`: iterable of selector values.

The `SelectorSQL` class additionally has the following initialization parameters:

* `sql (str)`: SQL statement that is sent to the database defined in `db.py`. The
statement should return a list of selections, for example:
`"select distinct linenumber from lines"`. The string can include
[Jinja2](https://pypi.org/project/Jinja2/)-expressions to read the `data` dictionary of
the `MapType`. This allows to use the selected values of another selector inside the SQL
query. For example, the list of bus stops can be limited to those stops, that lie within
the selected district (see [The MapType Class](map_type.md#example) for a code example).
You can also use other features of `Jinja2`, for example to express if-else-conditions.

* `additional_values (Iterable[Any], optional)`: iterable of additional choices that are
prepended to the values obtained via SQL, e.g. `["ALL"]`. Condition: the SQL statement
returns at least one element. Otherwise, the additional values are not prepended.

* `provide_raw_options (Boolean, optional)`: Adds a new entry to the data dictionary of
the associated `MapType`. It has as the label of the selector with appended
`" OPTIONS"` as key and all available options as value, regardless of which one was
selected in the UI. Default `False`.

## `MultiSelector` class

In addition to the two classes derived from `BaseSelector` there is the
`MultiSelector` class available. It can be used to combine multiple selectors.
These selectors should have mutually exclusive dependencies (defined with
`depends on_selectors`). The first selector passed via the `selectors` list,
which returns a value not equal to `None` is used to create an entry in the `data`
dictionary, with the `label` of the `MultiSelector` as key.

The `MultiSelector` class is initialized with the following parameters:

* `label (str)`: name of the selector. Will be displayed in the UI.

* `selectors (List[BaseSelector])`: list of `BaseSelector` objects, see above.

* `exclude_from_filename (bool, optional, default False)`: If `True`, the selector's
* value(s) will not be used to generate the filename.

In the following example, the selector "Stops a" will be shown, if no lines are
selected (empy list), the selector "Stops b" will be shown otherwise:

```python
MultiSelector(
    "Stops,
    [
        SelectorSimple(
            "Stops a",
            ["All", "None"],
            st.radio,
            depends_on_selectors={
                "Lines in the municipality": [],
                "Lines in district": [],
            },
            label_ui="Stops",
        ),
        SelectorSimple(
            "Stops b",
            ["All", "Stops served", "None"],
            st.radio,
            depends_on_selectors=[
                "Lines in the municipality",
                "Lines in district",
            ],
            label_ui="Stops",
        ),
    ],
),
```
