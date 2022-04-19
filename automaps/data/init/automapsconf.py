from db import db

# TODO: Add your MapType objects
MAPTYPES_AVAIL = []

# TODO: Add your QGIS installation path, e.g. '/usr'
# The path can be determined by opening up the QGIS GUI and running
# QgsApplication.prefixPath() in the Python console.
QGIS_INSTALLATION_PATH = ""

# TODO: Add the path to your QGIS project (qgz or qgs file)
FILEPATH_QGIS_PROJECT = "./some_file_name.qgz"

# TODO: Specify the path where the log file should be written
LOG_PATH = "./some_file_name.log"

# TODO: Add a project title
PROJECT_TITLE = "Some project title"

# TODO: Add page title
PAGE_TITLE = "Some page title"

PORT_MAP_SERVER = 5656
PORTS_WORKERS = [5656, 5657]
PORT_REGISTRY = 5757

# LOG_LEVEL_SERVER = "DEBUG"
# LOG_FORMAT = ""
# DOWNLOADS_RETAIN_TIME = 3600 * 12
# STATIC_PATH = ""
# LOGO_PATH = ""
# FAVICON_PATH = ""
# MAPTYPE_TEXT = ""
# MISSING_ATTRIBUTES_TEXT = ""
# CREATE_MAP_BUTTON_TEXT = ""
# WAITING_FOR_SERVER_TEXT = "Waiting for map server ..."
# NO_SERVER_AVAILABLE_TEXT = "Kartenserver ist ausgelastet. Bitte später noch einmal probieren!"
# SPINNER_TEXT = "Creating map _{maptype_name}_ ({step})"
# MAP_READY_TEXT = "Map _{maptype_name}_ is ready"
# SHOW_DEBUG_INFO = True
# CUSTOM_HTML = """
#     <style>
#     </style> """
# DOWNLOAD_BUTTON_STYLE = """
#     <style>
#         #{button_id} {{
#         }}
#         #{button_id}:hover {{
#         }}
#         #{button_id}:active {{
#         }}
#         #{button_id}:focus:not(:active) {{
#         }}
#     </style> """
