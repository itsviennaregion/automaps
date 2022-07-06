# The main configuration

This section describes the structure and options of the main configuration of an
automaps project.

When initilizing a new project (see section [Command Line Interface](cli.md))
a default configuration file is created in the project folder. The configuration is done
in a simple Python module. This allows a flexible setup, e.g. by splitting the
configuration into multiple files and importing them into the main module. The module
needs to be called `automapsconf.py`.

## Mandatory configuration

The following mandatory options need to been set:

* `MAPTYPES_AVAIL (List[MapType])`: This list needs to contain at least one instance of
a `MapType` class. The `MapType` objects mainly hold information about the UI elements
and their relationship with the project's input data. For further information see
section [The `MapType` class](map_type.md).

* `QGIS_INSTALLATION_PATH (str)`: This string variable holds a path to your QGIS installation, e.g. `"/usr"`. The path can be determined by opening up the QGIS GUI and
running `QgsApplication.prefixPath()` in the Python console.

* `FILEPATH_QGIS_PROJECT (str)`: This string variable holds the path to the QGIS
project associated with your autoMaps project (qgz or qgs file), e.g.
`"./some_file_name.qgz"`. See section [The QGIS project](qgis_project.md)
for further information.

* `LOG_PATH (str)`: This string variable holds the path where the log file should be
written, e.g. `"./some_file_name.log"`.

* `PORTS_WORKERS (List[int])`: The ZeroMQ ports of the worker processes as a list of
integers.

* `PORT_REGISTRY (int)`: The ZeroMQ port of the registry as an integer.

* `db (dict)`: The configuration of the database connection. It has to be a dictionary
which can be converted into an [SQLAlchemy `URL` object](https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.engine.URL).

## Optional configuration

### User Interface

#### General

* `PROJECT_TITLE (str)`: This string variable sets the project title. The title will be
shown in the sidebar menu. If the variable is not set, no title will be shown.

* `PAGE_TITLE (str)`: This string variable sets the page title, which will be shown in
the browser tab. If the variable is not set, Streamlit's default title is used.

* `SHOW_DEBUG_INFO (Optional[bool])`: If `True`, a debug section is added to the user
interface. If not set, no debug section will be shown.

#### Static content

* `STATIC_PATH (str)`: The path to the directory containing static files for the user
interface (logo or favicon images, help sites etc.). Typically, this is a subdirectory
of your autoMaps configuration. All content of the directory is then copied to
Streamlit's download directory as a subdirectory `static_automaps` to be available for
the frontend process. If not set, no content will be copied.

* `LOGO_PATH (Optional[str])`: The path to the logo of your project. Must start with
`./static_automaps/` to be accessible by the frontend. Use the `STATIC_PATH` config
option for automatically copying files from your configuration directory to Streamlit`s
static directory. If not set, no logo will be shown.

* `FAVICON_PATH (Optional[str])`: The path to the favicon of your project. Must start
with `./static_automaps/` to be accessible by the frontend. Use the `STATIC_PATH` config
option for automatically copying files from your configuration directory to Streamlit`s
static directory. If not set, Streamlit`s default favicon will be shown.

#### Texts

* `MAPTYPE_TEXT (Optional[str])`: Text to be shown above the radio buttons in the side
bar. If not set, the text "Map type" will be shown.

* `MISSING_ATTRIBUTES_TEXT (Optional[str])`: Text to be shown, if not all necessary
map attributes are defined in the user interface. If not set, the text "Please define
all required map attributes!" will be shown.

* `CREATE_MAP_BUTTON_TEXT (Optional[str])`: Text to be shown on the button which starts
the map creation process. If not set, the text "Create map" will be used.

* `WAITING_FOR_SERVER_TEXT (Optional[str])`: Text to be shown, while the frontend
process is wating for an idle worker. If not set, the text "Waiting for map server ..."
will be shown.

* `NO_SERVER_AVAILABLE_TEXT (Optional[str])`: Text to be shown, if after some time no
idle worker has been found to process the map creation request. If not set, the text
"Map server is busy, please retry later!" will be used.

* `SPINNER_TEXT (Optional[str])`: (Markdown) text to be shown by the Streamlit spinner
while the map creation request is processed by a worker. You can include two variables
(`maptype_name` and `step`) in the text. If not set, it defaults to
`"Creating map _{maptype_name}_ ({step})"`.

* `MAP_READY_TEXT (Optional[str])`: (Markdown) text to be shown after the map creation
process has been finished. You can include the varible `maptype_name` in the text. If
not set, it defaults to `"Map _{maptype_name}_ ready"`.

#### Styling

* `CUSTOM_HTML (Optional[str])`: Custom HTML which will be injected at the top of the
Streamlit page. Its main use is to change the page styling. If not set, no HTML will be
injected. You may set the config option to something like:

```css
<style>
    h1 {
        padding-top: 0.2rem;
    }
    footer {
        visibility: hidden;
        display: none;
    }
    strong {
        font-weight: 800;
    }
</style>
```

* `DOWNLOAD_BUTTON_STYLE (Optional[str])`: Custom HTML which will be injected right
above the download button. Its main use is to change the button styling. Use the css
identifier `#{button_id}` for this purpose. If not set, a simple default style will
be used. You may set the config option so something like:

```css
<style>
    #{button_id} {{
        background-color: #99cc00;
        color: rgba(0,0,0,0.87);
        border: 0;
        padding: 0.35em 0.58em;
        position: relative;
        text-decoration: none;
        border-radius: 0.25rem;
    }}
    #{button_id}:hover {{
        background-color: #649b00;
    }}
    #{button_id}:active {{
        background-color: #99cc00;
        }}
    #{button_id}:focus:not(:active) {{
        background-color: #99cc00;
        }}
</style>
```

### Backend

* `LOG_LEVEL_SERVER (str)`: This string variable sets the backend server's log level.
It needs to be one of Python's `logging` modules levels, like `DEBUG`. If not set,
the log level defaults to `DEBUG`.

* `PORT_LOGGER_SERVER (int)`: The ZeroMQ port of the logger server as an integer. Be
sure to put this on top of your configuration file, if activated!

* `LOG_FORMAT (str)`: The log format (see
[Python Docs](https://docs.python.org/3/library/logging.html)). If not set,
`"%(asctime)s -- %(levelname)-7s -- %(name)s -- %(message)s"` will be used.

* `DOWNLOADS_RETAIN_TIME (Optional[int])`: Maximum age of map export files to be kept in
the download directory, in seconds. Older files will be deleted. If not set, it defaults
to 8 hours.
