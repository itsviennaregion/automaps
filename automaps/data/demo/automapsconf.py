from automapsconf_poly import maptype_poly
from db import db

MAPTYPES_AVAIL = [maptype_poly]

PORTS_WORKERS = [4646, 4647]
PORT_REGISTRY = 4747

QGIS_INSTALLATION_PATH = "/usr"
FILEPATH_QGIS_PROJECT = "./demo_project.qgz"
LOG_PATH = "./demo_project.log"
# LOG_FORMAT = "%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s"
LOG_LEVEL_SERVER = "DEBUG"
# STATIC_PATH = ""

DOWNLOADS_RETAIN_TIME = 3600 * 12

# LOGO_PATH = ""
# FAVICON_PATH = ""
PROJECT_TITLE = "Automaps Demo Project"
PAGE_TITLE = "Automaps Demo Project"
# MAPTYPE_TEXT = ""
# MISSING_ATTRIBUTES_TEXT = ""
# CREATE_MAP_BUTTON_TEXT = ""
# WAITING_FOR_SERVER_TEXT = "Warte auf Kartenserver ..."
# NO_SERVER_AVAILABLE_TEXT = "Kartenserver ist ausgelastet. Bitte später noch einmal probieren!"
# SPINNER_TEXT = "Creating map _{maptype_name}_ ({step})"
# MAP_READY_TEXT = "🎉 🗺 🧭 🚌 🚊 🚂 🚂 🚊 🚌 🧭 🗺 🎉\n\Map _{maptype_name}_ is ready\n\n🎉 🗺 🧭 🚌 🚊 🚂 🚂 🚊 🚌 🧭 🗺 🎉"
SHOW_DEBUG_INFO = True
CUSTOM_HTML = """
    <style>
        h1 {
            padding-top: 0.2rem;
        }
        footer {
            visibility: hidden;
            display: none;
        }
        strong {
            font-weight: 500;
        }
    </style> """
DOWNLOAD_BUTTON_STYLE = """
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
    </style> """
