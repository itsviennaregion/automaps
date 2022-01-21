# Prepare sys.path to allow loading user config with 'import automapsconf'
import sys

conf_path, automaps_path = sys.argv[1:]
if conf_path not in sys.path:
    sys.path.insert(0, conf_path)
if automaps_path not in sys.path:
    sys.path.append(automaps_path)

import logging
import os
import pathlib
import traceback

import streamlit as st

from automaps.fileserver import (
    download_button,
    DownloadPathJanitor,
    get_streamlit_download_path,
    create_streamlit_download_path,
)
from automaps.client.client import ask_server_for_steps, send_task_to_server
from automaps.confutils import get_config_value, get_default_args, has_config_option
import automapsconf
from automapsconf import MAPTYPES_AVAIL


def _get_maptype_names():
    return [x.name for x in MAPTYPES_AVAIL]


def _get_maptype(name: str):
    for maptype in MAPTYPES_AVAIL:
        if name == maptype.name:
            return maptype


def start_frontend():
    _init()

    # Delete old files in download path
    if hasattr(automapsconf, "DOWNLOADS_RETAIN_TIME"):
        j = DownloadPathJanitor(
            get_streamlit_download_path(), automapsconf.DOWNLOADS_RETAIN_TIME
        )
    else:
        j = DownloadPathJanitor(get_streamlit_download_path())
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
    st.write(f"# {maptype.name}{maptype.html_beneath_name}", unsafe_allow_html=True)
    st.write(f"{maptype.description}", unsafe_allow_html=True)

    # Show widgets if conditions defined by Selector argument `depends_on_selectors`
    # are satisfied) and get selected values
    selector_values = maptype.selector_values

    # Create map
    if st.button(get_config_value("CREATE_MAP_BUTTON_TEXT", "Create map")):
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


def _init():
    if not hasattr(automapsconf, "init_done"):
        create_streamlit_download_path()
        logging.info("Automaps initialized!")
        logging.info(f"  Download path: {get_streamlit_download_path()}")
        max_seconds = (
            automapsconf.DOWNLOADS_RETAIN_TIME
            if hasattr(automapsconf, "DOWNLOADS_RETAIN_TIME")
            else get_default_args(DownloadPathJanitor.__init__)["max_seconds"]
        )
        logging.info(
            f"  Downloads are retained for {max_seconds} seconds "
            f"({max_seconds / 3600:.1f} hours)."
        )

        automapsconf.init_done = True


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
    if has_config_option("PAGE_TITLE"):
        st.set_page_config(page_title=automapsconf.PAGE_TITLE)


def _show_project_title():
    if has_config_option("PROJECT_TITLE"):
        st.sidebar.markdown(f"# {automapsconf.PROJECT_TITLE}")
        st.sidebar.markdown("#")


def _add_custom_html():
    if has_config_option("CUSTOM_HTML"):
        st.markdown(automapsconf.CUSTOM_HTML, unsafe_allow_html=True)


def _show_debug_info(selector_values):
    if get_config_value("SHOW_DEBUG_INFO"):
        # Show selected values for all widgets (for debugging)
        if st.checkbox("Debug"):
            st.write("## Debug Info")
            for k, v in selector_values.items():
                st.write(f"{k}: __{v}__")


if __name__ == "__main__":
    start_frontend()
