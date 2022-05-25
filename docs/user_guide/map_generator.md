# The `MapGenerator` Class

[API docs](../api/generators.md)

Each map type of an autoMaps project needs to consist of:

* a `MapType` object (see [this](map_type.md) section)
* a generator class (a subclass of `MapGenerator`), described here
* one or more QGIS print layouts in an associated QGIS project file (see
[this](qgis_project.md) section)

Each generator class needs to be a subclass of `automaps.generators.base.MapGenerator`.

Each generator class needs a class attribute `name`, a method `_set_steps()`,
and freely definable methods for map generation.

The method `_set_steps()` must itself set the attribute `self.steps` of type
`OrderedDict[str, Step]`.

As keys of the `OrderedDict`, speaking names of the processing step should be
assigned. These are also displayed in the frontend for information about the
processing progress. The processing is carried out in the ordered of the items in the
`OrderedDict`.

As values of the `OrderedDict`, `NamedTuples` of type `Step` are expected, with the
following attributes:

* `func (Callable)` is the method defined in the class that executes the step.
* `weight (float)` is the relative weight of the step with respect to the expected
processing time (relative to the other steps).This is used to display the progress bar
in the frontend.

!!! info

    For each execution of a step a new instance of the `MapGenerator` is created! The
    attribute `self` can therefore not be used to pass data between steps. Instead, the
    attribute `step_data` of type `StepData` should be used (take a look at the example
    below). For this purpose, attributes can be added freely to the `step_data` object.

During initialization, the associated QGIS project (defined with the config option
`FILEPATH_QGIS_PROJECT`) and the print layout (defined with the argument `print_layout`).
in the configuration of the associated `MapType` in `/automapsconf.py`) are loaded.
These to objects are stored in `self.step_data.project` and `self.step_data.layout`,
respectively, and are thus available for all processing steps.

For example, a small generator class with four steps could look like this:

```python
from collections import OrderedDict

from automaps.generators.base import MapGenerator, Step


class MapGeneratorPoly(MapGenerator):
    name = "Districts in Vienna"

    def _set_steps(self):
        self.steps = OrderedDict(
            {
                "Initialize project": Step(self.init_project, 1),
                "Filter layers": Step(self.filter_layers, 1),
                "Zoom to extent": Step(self.set_extent, 1),
                "Export map": Step(self.export_layout, 5),
            }
        )

    def init_project(self):
        self._init_layers()
        self._set_project_variable("data", self.data)
        self._set_map_layer_visibility("districts", True)
        self._set_map_layer_visibility("OpenStreetMap", True)
        self.step_data.district_filter = f"NAMEK = '{self.data['District name']}'"

    def filter_layers(self):
        self._set_map_layer_filter_expression(
            "districts", self.step_data.district_filter
        )

    def set_extent(self):
        self._zoom_map_to_layer_extent("Map 1", self._get_map_layer("districts"))

    def export_layout(self):
        self._export_print_layout()
        self.step_data.project.write("./poly_out.qgz")
        del self.step_data.project
```
