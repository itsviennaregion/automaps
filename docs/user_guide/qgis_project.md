# The QGIS Project

Each map type of an autoMaps project needs to consist of:

* a `MapType` object (see [this](map_type.md) section)
* a generator class (a subclass of `MapGenerator`) (see [this](map_generator.md)
section)
* one or more QGIS print layouts in an associated QGIS project file (described here)

The main configuration `automapsconf.py` of an autoMaps project references a QGIS
project via its `FILEPATH_QGIS_PROJECT` option
(see [Main Configuration](main_config.md)). This project is used to bring all the
geodata together, to define the symbology, the labels etc. Details on this process
are beyond the scope of this user guide but can be found in the
[QGIS docs](https://qgis.org/en/docs/index.html).

At least one QGIS print layout is needed to export maps with autoMaps. It is linked
to the [MapType](map_type.md) via its `print_layout` argument.

Before the map export is executed, the associated QGIS project is automatically loaded
into memory by autoMaps and modified by the processing steps of the respective
[MapGenerator](map_generator.md). This way, the sophisticated cartographic capabilities
of QGIS can be used to prepare the general styling and layout, which is then used to
create a concrete map as defined by the user. Take a look at the description of the
[demo project](../getting_started.md#exploring-the-demo-project) to get an impression
of this workflow.
