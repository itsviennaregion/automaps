## The `MapGenerator` class

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
        self._export_print_layout()
```