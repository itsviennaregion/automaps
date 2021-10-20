# automaps

![](static/teaser.webm)

## Short description
__TODO__

## Architecture
__TODO__

## Installation
* Install QGIS (https://qgis.org/en/site/forusers/download.html)
* Clone this repository:

    `git clone https://gitlab.com/its-vienna-region/digilab/automatisierte-karten`

* Change into the cloned directory:

    `cd automatisierte-karten`

* Install the `automaps` package (__for the Python interpreter used by QGIS!__): 

    `python3 -m pip install .`


## Create a demo project

__TODO__

## Start the Streamlit frontend + QGIS backend.
Execute from:

`./start_automaps.sh`. 

Possibly before:

`chmod +x start_automaps.sh`

The frontend is accessible at [http://localhost:8505/vormaps](http://localhost:8505/vormaps)
accessible. 

## Configuration
The following files and directories are relevant for the configuration:

    /conf.py
    /conf_local.py
    /conf_server.py
    /generators

### `/conf.py`
Here the configuration of the frontend and the map generation must be done in the variable
MAPTYPES_AVAIL` variable. This is a dictionary with the 
structure `Dict[str, MapType]`. 

As key of the dictionary a designation of the map type is to be assigned. This 
is displayed in the frontend for selection. 

MapType
is initialized with the following arguments: 
* `name (str)`: Name of the map type. This must be used as a key in the variable `GENERATORS`. 
in `/conf_server.py` (see below).
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

Example:
``python
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

The configuration of the selection options displayed in the UI is done with the help of
`Selector` objects.

__`BaseSelector` classes__

Two selector classes derived from `selector.BaseSelector` are available:

* `SelectorSimple`: For lists of choices (e.g. "bus" or "train"),
which are defined directly in `conf.py`.
* `SelectorSQL`: For lists of selections that are formed based on a database
database query.

These `Selector` classes share the following parameters for initialization:
* `label (str)`: name of the selector. Displayed in the UI. Furthermore
the label can be used to define dependencies between the selectors of a `MapType` (see parameter `depend
(see `depends_on_selectors` parameter).
* `widget_method (Callable, optional)`: One of the widgets provided by streamlit 
(e.g. st.radio or st.selectbox). If no argument or `None` is passed, no widget will be used in the
UI, no widget for selecting values will be displayed. The list of options created (e.g. by an SQL query)
will still be available and can be edited via the `self.data` attribute. 
`self.data` attribute of the associated `MapType`. With this mechanism
can be used to execute SQL queries in the background, the results of which cannot be
visible and selectable in the UI, but can be used by subsequent selectors. 
selectors.
* `widget_args (dict, optional)`: dictionary of arguments passed to initialize the widget object.
of the widget object (e.g. `{"help"="help text"}`).
* `no_value_selected_text (str, optional)`: selection option to be displayed,
before a value has been selected (e.g. "Select spatial layer ...").
* `depends_on_selectors (Union[List[str], Dict[str, Any]], optional)`: 
This can be used to define conditions that must be met for the widget to be
is displayed. This can be used to define dependencies between selectors. 
Either a list or a dictionary can be passed:

    * __Dictionary__: 
As keys must be the labels
of selectors also defined for the same `MapType` must be used as keys, as
Values the values that must be selected for the corresponding selector. If
e.g. the value "line" must be selected for the selector with the label "spatial layer", then `depends
then `depends_on_selectors={"Spatial layer": "Line"}` must be set. Currently
can only be checked for equality. If the dictionary contains more than one key/value pairs
only one of the conditions must be met (OR operation).

    * __list__:
A list of selector labels of selectors of the same `MapType`. If the 
corresponding selectors contain either `None` or the default text 
(`no_value_selected_text`) as value, the widget will not be displayed.
For example, a selector for public transport lines can only be displayed if first
a municipality has been selected (`depends_on_selectors=["municipality"]`). If the list
list contains multiple selector labels, the widget will be displayed as soon as one of the listed
listed selectors has a value selected (OR operation).
* `label_ui (str, optional)`: Alternative label of the widget to be displayed in the UI.
should be displayed.
* `optional (bool, optional, default False)`: Indicates whether the widget is optional, i.e. whether
map generation can be started even though the widget has the default value of
(`no_value_selected_text`) or an empty list as result. Has influence
on setting the `has init values` flag in the associated `MapType`.
* `exclude_from_filename (bool, optional, default False)`: If `True` then the
value(s) of the selector will not be used to generate the filename. 

The `SelectorSimple` class is also initialized with the following parameter 
initialized:
* `options (Iterable[Any])`: iterable of selectors.

The `SelectorSQL` class additionally has the following 
initialization parameters:
* `sql (str)`: SQL statement that is sent to the database defined in `db.ini
and should return a list of selections, for example: `"select distinct 
linenumber from lines"`. The string can be 
[Jinja2](https://pypi.org/project/Jinja2/)-expressions to read the 
`data` dictionary with the selecting UI options. 
This allows the selected values of a selector defined in `MapType` as `ui_element` to be used in the SQL 
can be used in the SQL query of another selector. In 
the selection of bus lines can be limited to those lines that intersect the selected municipality. 
which intersect the selected municipality. For an example see above at 
`MapType`. 
* `additional_values (Iterable[Any], optional)`: iterable of additional 
choices that are prepended to the values obtained via SQL,
e.g. `["ALL"]`.
* `provide_raw_options (Boolean, optional)`: The data dictionary of the associated
MapType` a new entry can be added. This has as key the 
selector with appended `" OPTIONS"` as key and all available options as value. 
options available, regardless of which one was selected in the UI. Default `False`. 

__`MultiSelector` class__

In addition to the two classes derived from `BaseSelector` there is the
MultiSelector` is available. This can be used to combine multiple selectors.
These selectors should have mutually exclusive dependencies (defined with `depends 
with `depends_on_selectors`). The first selector passed via the `selectors` list,
which returns a value not equal to `None` is used to create an entry in the `data` dictionary
with the `label` of the `MultiSelector` as key.

The `MultiSelector` class is initialized with the following parameters:
* `label (str)`: name of the selector. Will be displayed in the UI. 
* `selectors (List[BaseSelector])`: list of `BaseSelector` objects, see above.
* `exclude_from_filename (bool, optional, default False)`: If `True`, then the selector's
value(s) of the selector will not be used to generate the filename. 

Example:

```python
MultiSelector(
    "`stops`,
    [
        SelectorSimple(
        "Stops a",
        ["All", "None"],
        st.radio,
        depends_on_selectors={
            "Lines in the municipality": [],
            "lines in district": [],
            "lines in tender region": [],
            "Lines in State": [],
        },
        label_ui="stops",
    ),
    SelectorSimple(
        "Stops b",
        ["All", "Stops served", "None"],
        st.radio,
        depends_on_selectors=[
            "Lines in the municipality",
            "Lines in district",
            "Lines in tender region",
            "lines in state",
        ],
        label_ui="Stops",
    ),
],
),
```

### `/conf_local.py`
The following variables must be set here:

The directory path to store the generated maps (`BASEPATH_FILESERVER`), for example:

    BASEPATH_FILESERVER = `usr/local/lib/python3.8/dist-packages/streamlit/static/downloads`.

The directory path to the QGIS installation (`QGIS_INSTALLATION_PATH`). This can be set in the 
QGIS GUI in the Python Console with the following command:
`QgsApplication.prefixPath()`. Example:

    QGIS_INSTALLATION_PATH = "/usr".

The file path to the QGIS project file (`FILEPATH_QGIS_PROJECT`), for example:

    FILEPATH_QGIS_PROJECT = "/home/automaps/automaps_qgis/automaps_dev.qgz"

### `/conf_server.py`
The following variables must be set here:

The variable `GENERATORS` of type `Dict[str, MapGenerator]`. The keys to be used are those specified in 
`/conf.py` must be used as the `name` attributes of the `MapType` objects. As
values the corresponding map generators with the base class `MapGenerator`. 
(see below, `/generators`)

Example for `/conf_server.py`:

    from typing import Dict

    from automaps.generators import MapGeneratorOverview
    from automaps.generators.base import MapGenerator

    GENERATORS: Dict[str, MapGenerator] = {"public transport overview": MapGeneratorOverview}


### `/generators`
Here the individual map generators are created as a subclass of `MapGenerator` (to be found in 
in `/generators/base.py`).

For this purpose a new Python module is created in the package `generators`. This contains
the class definition of the generator. 

Each generator class needs a class attribute `name`, a method `_set_steps()`
and freely definable methods for map generation. 

The method `_set_steps()` must have the attribute `self.steps` of type 
`OrderedDict[str, Step]`. As keys speaking names of the 
processing step should be assigned as keys. These are also displayed in the frontend for information
about the processing progress. The processing is carried out in the 
`OrderedDict` order.

NamedTuples of type `Step` are expected as values, with the following attributes:
* `func (Callable)` is the method defined in the class that executes the step.
* `weight (float)` is the relative weight of the step with respect to the expected processing time (relative to the other steps).
  processing time (relative to the other steps of a map generator). This
  is used to display the progress bar in the frontend.

__Attention!__: For each execution of a step a new instance of the
`MapGenerator` is created! The attribute 'self' can therefore not be used to pass data between steps. 
between the steps. Instead, the attribute `step_data` 
of type `StepData` can be used instead, as can be seen in the example. For this purpose any attributes can be added to the
object any attributes can be added.

During initialization the associated QGIS project (defined in 
`/conf_local.py`) and the print layout (defined with the argument `print_layout`).
in the configuration of the associated `MapType` in `/conf.py`) are loaded. The two 
loaded objects are stored in `self.step_data.project` and `self.step_data.layout` and are 
and are available there for all processing steps.

For example, a small generator class with three steps could look like this: 

```python
from collections import OrderedDict

from automaps.generators.base import MapGenerator, Step


class MapGeneratorUeberblick(MapGenerator):
    name = "ÖV-Überblick"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Projektvariablen setzen": Step(self.set_variables, 1),
                "Layer filtern": Step(self.filter_layers, 1),
                "Kartenausschnitt festlegen": Step(self.set_extent, 1),
                "Karte exportieren": Step(self.export_layout, 3),
            }
        )

    def set_variables(self):
        self._set_project_variable("gemeinde_aktiv", self.data["Gemeinde"])

    def filter_layers(self):
        self._set_map_layer_filter_expression(
                "bev_gemeinden", f"pg = '{self.data['Gemeinde']}'"
            )
    
    def set_extent(self):
        self._zoom_map_to_layer_extent(
            "Hauptkarte", self._get_map_layer("bev_gemeinden")
        )

    def export_layout(self):
        self._export_print_layout(self.step_data.layout)
```

## Kartenlayer


### Steig Betriebszweig
```sql
-- drop view automaps_lin;
create or replace view automaps_lin as
select
    row_number () over (),
	lin.subnetwork,
    lin.opbranch,
    lin.fromstopid,
    lin.fromstopar,
    lin.fromstoppi,
    lin.tostopid,
    lin.tostopar,
    lin.tostoppi,
    lin.linediva,
    lin.lineefa,
    lin.project,
    lin.direction,
    lin.sequenceno,
    lin.geom::geometry(Linestring, 32633) as geom,
	bz.kurzbezeichnung kurz,
	case
		when bz.kode in (1, 4, 5, 6, 7, 9, 10)  then 'Bahn'
		when bz.kode in (21, 31)  then 'U-Bahn'
		when bz.kode in (11, 22, 32)  then 'Tram'
		when bz.kode in (23, 24, 33, 34, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 76, 77, 79, 81, 82, 86, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99)  then 'Bus'
		when bz.kode in (8, 25, 35, 73)  then 'Mikro V'
		else 'Unbekannt'
	end typ
from ptlinks_ptl_polyline lin
left join betriebszweige bz on bz.kode = lin.opbranch
;
```

### Steig Betriebszweig
```sql
-- drop view automaps_stg;
-- drop view automaps_hst;
-- drop view automaps_stg_class;
create or replace view automaps_stg_class as
select distinct
	stopid,
    stopareaid,
    stoppingpo,
	array_agg(lin_id) linien,
	array_agg(distinct kurz),
	case
		when array_agg(kode) && array[1, 4, 5, 6, 7, 9, 10]  then 'Bahn'
		when array_agg(kode) && array[21, 31]  then 'U-Bahn'
		when array_agg(kode) && array[11, 22, 32]  then 'Tram'
		when array_agg(kode) && array[23, 24, 33, 34, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 76, 77, 79, 81, 82, 86, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]  then 'Bus'
		when array_agg(kode) && array[8, 25, 35, 73]  then 'Mikro V'
		else 'Unbekannt'
	end typ
from (
select
	lin.fromstopid stopid,
	lin.fromstopar stopareaid,
	lin.fromstoppi stoppingpo,
	lin.lineefa lin_id,
	bz.kurzbezeichnung kurz,
	bz.kode
from ptlinks_ptl_polyline lin
left join betriebszweige bz on bz.kode = lin.opbranch
union
select
	lin.tostopid stopid,
	lin.tostopar stopareaid,
	lin.tostoppi stoppingpo,
	lin.lineefa lin_id,
	bz.kurzbezeichnung kurz,
	bz.kode
from ptlinks_ptl_polyline lin
left join betriebszweige bz on bz.kode = lin.opbranch
) unioned
group by
	stopid,
    stopareaid,
    stoppingpo
;
```

### Steig
```sql
-- drop view automaps_stg;
create or replace view automaps_stg as
select
    stg.subnetwork,
    stg.stopid,
    stg.stopareaid,
    stg.stoppingpo,
    stg.drawclass,
    stg.name1,
    stg.name2,
    stg.globalid,
    stg.servingsta,
    stg.geom::geometry(Point, 32633) as geom,
    hst.name1 as hst_name,
    st_x(hst.geom) as hst_x,
    st_y(hst.geom) as hst_y,
    cla.typ,
    cla.linien
from stoppingpoints_stp_point stg
left join stops_stp_point hst on stg.stopid = hst.stopid
left join automaps_stg_class cla on stg.stopid = cla.stopid 
    and stg.stopareaid = cla.stopareaid 
    and stg.stoppingpo = cla.stoppingpo
;
```

### Haltestelle
```sql
-- drop view automaps_hst;
create or replace view automaps_hst as
select
    hst.subnetwork,
    hst.stopid,
    hst.drawclass,
    hst.name1,
    hst.name2,
    hst.tarifzone,
    hst.attributes,
    hst.servinglin,
    hst.globalid,
    hst.servingsta,
    hst.name0,
    hst.geom::geometry(Point, 32633) as geom,
    case
        when array_agg(cla.typ) && array['Bahn']  then 'Bahn'
		when array_agg(cla.typ) && array['U-Bahn']  then 'U-Bahn'
		when array_agg(cla.typ) && array['Tram']  then 'Tram'
		when array_agg(cla.typ) && array['Bus']  then 'Bus'
		when array_agg(cla.typ) && array['Mikro V']  then 'Mikro V'
		else 'Unbekannt'
	end typ
from stops_stp_point hst
left join automaps_stg_class cla on hst.stopid = cla.stopid
group by
	hst.subnetwork,
    hst.stopid,
    hst.drawclass,
    hst.name1,
    hst.name2,
    hst.tarifzone,
    hst.attributes,
    hst.servinglin,
    hst.globalid,
    hst.servingsta,
    hst.name0,
    hst.geom
;
```
