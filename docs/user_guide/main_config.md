# The main configuration

This section describes the structure and options of the main configuration of an 
automaps project.

When initilizing a new project (see section [Command Line Interface](cli.md))
a default configuration file is created in the project folder. The configuration is done
in a simple Python module. This allows a flexible setup, e.g. by splitting the 
configuration into multiple files.

## Mandatory configuration

The following mandatory options need to been set:

* `MAPTYPES_AVAIL (List[MapType])`: This list needs to contain at least one instance of
a `MapType` class. The `MapType` objects mainly hold information about the UI elements
and their relationship with the project's input data. For further information see 
section [The `MapType` class](map_type.md).

* `QGIS_INSTALLATION_PATH (str)`: This string variable holds a path to your QGIS installation, e.g. `"/usr"`. The path can be determined by opening up the QGIS GUI and 
running QgsApplication.prefixPath() in the Python console.

* `FILEPATH_QGIS_PROJECT (str)`: This string variable holds the path to the QGIS 
project associated with your autoMaps project (qgz or qgs file), e.g.
`"./some_file_name.qgz"`. See section [The QGIS project](qgis_project.md)
for further information.

* `LOG_PATH (str)`: This string variable holds the path where the log file should be 
written, e.g. `"./some_file_name.log"`.

* `PORT_MAP_SERVER (int, defaults to 5656)`: This integer variable sets the port for
the communication between frontend and backend processes. If you have no reason to 
change it, leave the default as it is.

* `PORTS_WORKERS`: TODO

* `PORT_REGISTRY`: TODO

## Optional configuration
### User Interface
* `PROJECT_TITLE (str)`: This string variable sets the project title. The title will be
shown in the sidebar menu. If the variable is not set, no title will be shown.

* `PAGE_TITLE (str)`: This string variable sets the page title, which will be shown in
the browser tab. If the variable is not set, Streamlit's default title is used.

### Backend

* `LOG_LEVEL_SERVER (str)`: This string variable sets the backend server's log level.
It needs to be one of Python's `logging` modules levels, like `DEBUG`. If not set,
the log level defaults to `DEBUG`.

* `LOG_FORMAT (str)`: TODO

* `STATIC_PATH (str)`: TODO


from typing import List

from automaps.maptype import MapType

SHOW_DEBUG_INFO: bool
PORT_MAP_SERVER: int
QGIS_INSTALLATION_PATH: str
DOWNLOADS_RETAIN_TIME: int
LOGO_PATH: str
FAVICON_PATH: str
PROJECT_TITLE: str
PAGE_TITLE: str
MAPTYPE_TEXT: str
MISSING_ATTRIBUTES_TEXT: str
CREATE_MAP_BUTTON_TEXT: str
WAITING_FOR_SERVER_TEXT: str
NO_SERVER_AVAILABLE_TEXT: str
SPINNER_TEXT: str
MAP_READY_TEXT: str
CUSTOM_HTML: str
DOWNLOAD_BUTTON_STYLE: str
FILEPATH_QGIS_PROJECT: str
db: dict