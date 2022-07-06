from typing import List, Optional

from automaps.maptype import MapType

LOG_PATH: str
PORT_REGISTRY: int
PORTS_WORKERS: List[int]
FILEPATH_QGIS_PROJECT: str
MAPTYPES_AVAIL: List[MapType]
QGIS_INSTALLATION_PATH: str
db: dict

PROJECT_TITLE: Optional[str]
PAGE_TITLE: Optional[str]
SHOW_DEBUG_INFO: Optional[bool]
LOG_FORMAT: Optional[str]
PORT_LOGGER_SERVER: Optional[int]
LOG_LEVEL_SERVER: Optional[str]
STATIC_PATH: Optional[str]
DOWNLOADS_RETAIN_TIME: Optional[int]
LOGO_PATH: Optional[str]
FAVICON_PATH: Optional[str]
MAPTYPE_TEXT: Optional[str]
MISSING_ATTRIBUTES_TEXT: Optional[str]
CREATE_MAP_BUTTON_TEXT: Optional[str]
WAITING_FOR_SERVER_TEXT: Optional[str]
NO_SERVER_AVAILABLE_TEXT: Optional[str]
SPINNER_TEXT: Optional[str]
MAP_READY_TEXT: Optional[str]
CUSTOM_HTML: Optional[str]
DOWNLOAD_BUTTON_STYLE: Optional[str]
