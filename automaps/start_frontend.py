# Prepare sys.path to allow loading user config with 'import automapsconf'
import sys

conf_path, automaps_path = sys.argv[1:]
if conf_path not in sys.path:
    sys.path.insert(0, conf_path)
if automaps_path not in sys.path:
    sys.path.append(automaps_path)

import os
import pathlib
import traceback

import streamlit as st

from automaps.fileserver import download_button, DownloadPathJanitor
from automaps.client.client import ask_server_for_steps, send_task_to_server
from automaps.confutils import get_config_value, has_config_option
import automapsconf
from automapsconf import MAPTYPES_AVAIL

STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()
    print(
        f"Download path '{DOWNLOADS_PATH}' has been created. Maybe you need to "
        f"change the permissions (e.g. sudo chmod -R a+w {DOWNLOADS_PATH})."
    )


def _get_maptype_names():
    return [x.name for x in MAPTYPES_AVAIL]


def _get_maptype(name: str):
    for maptype in MAPTYPES_AVAIL:
        if name == maptype.name:
            return maptype


def start_frontend():
    # Delete old files in download path
    j = DownloadPathJanitor(automapsconf.BASEPATH_FILESERVER)
    j.clean()

    # Add custom elements to UI
    _set_page_title()
    _show_logo()
    _show_project_title()
    _add_custom_html()

    # Show available map types and get selected value
    maptype_dict_key = st.sidebar.radio(
        get_config_value("MAPTYPE_TEXT", "Map type"), _get_maptype_names()
    )

    # Instantiate MapType object
    maptype = _get_maptype(maptype_dict_key)

    # Show information about the selected map type
    st.write(f"# {maptype.name}")
    st.write(f"{maptype.description}")

    # Show widgets if conditions defined by Selector argument `depends_on_selectors`
    # are satisfied) and get selected values
    selector_values = maptype.selector_values

    # Create map
    if st.button("Karte erstellen"):
        if selector_values.get("has_init_values", False):
            st.info(
                get_config_value(
                    "MISSING_ATTRIBUTES_TEXT",
                    "Please define all required map attributes!",
                )
            )
        else:
            try:
                progress_bar = st.progress(0)
                progress = 0
                with st.spinner(
                    get_config_value(
                        "WAITING_FOR_SERVER_TEXT", "Waiting for map server ..."
                    )
                ):
                    steps = ask_server_for_steps(maptype_dict_key)

                for step in steps:
                    with st.spinner(
                        get_config_value(
                            "SPINNER_TEXT", "Creating map _{maptype_name}_ ({step})"
                        ).format(maptype_name=maptype.name, step=step)
                    ):
                        step_message = send_task_to_server(
                            maptype_dict_key,
                            selector_values,
                            maptype.print_layout,
                            step,
                        )
                        progress += float(step_message["rel_weight"])
                        progress_bar.progress(progress)
                progress_bar.progress(1.0)
                st.success(
                    get_config_value(
                        "MAP_READY_TEXT", "Map _{maptype_name}_ ready"
                    ).format(maptype_name=maptype.name)
                )
                _show_download_button(step_message["filename"])

            except Exception as e:
                _show_error_message(e)

    _show_debug_info(selector_values)


def _show_download_button(filename: str):
    download_button_str = download_button(
        os.path.basename(filename),
        "Download",
    )
    st.markdown(download_button_str, unsafe_allow_html=True)


def _show_error_message(exception: Exception):
    st.error(f"Sorry, there has been an error: {exception}")
    tb = traceback.format_exc()
    st.error(tb)


def _show_logo():
    if has_config_option("LOGO_PATH"):
        st.sidebar.image(automapsconf.LOGO_PATH)


def _set_page_title():
    if has_config_option("PROJECT_TITLE"):
        st.set_page_config(page_title=automapsconf.PROJECT_TITLE)


def _show_project_title():
    if has_config_option("PROJECT_TITLE"):
        st.sidebar.markdown(f"# {automapsconf.PROJECT_TITLE}")
        st.sidebar.markdown("#")


def _add_custom_html():
    if has_config_option("CUSTOM_HTML"):
        st.markdown(automapsconf.CUSTOM_HTML, unsafe_allow_html=True)


def _show_debug_info(selector_values):
    if has_config_option("SHOW_DEBUG_INFO"):
        # Show selected values for all widgets (for debugging)
        if st.checkbox("Debug"):
            st.write("## Debug Info")
            for k, v in selector_values.items():
                st.write(f"{k}: __{v}__")


if __name__ == "__main__":
    start_frontend()
