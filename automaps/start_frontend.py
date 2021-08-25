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

from automaps.fileserver import download_button, download_link
from automaps.client.client import ask_server_for_steps, send_task_to_server
from automapsconf import MAPTYPES_AVAIL

STREAMLIT_STATIC_PATH = pathlib.Path(st.__path__[0]) / "static"
DOWNLOADS_PATH = STREAMLIT_STATIC_PATH / "downloads"
if not DOWNLOADS_PATH.is_dir():
    DOWNLOADS_PATH.mkdir()
    print(
        f"Downloadpfad '{DOWNLOADS_PATH}' wurde erstellt. Eventuell müssen noch die "
        f"Berechtigungen angepasst werden (z.B. sudo chmod -R a+w {DOWNLOADS_PATH})."
    )


def start_frontend():
    st.set_page_config(page_title="VOR Karten")
    _hide_footer()

    # Show available map types and get selected value
    maptype_dict_key = st.sidebar.radio("Kartentyp", list(MAPTYPES_AVAIL.keys()))

    # Instantiate MapType object
    maptype = MAPTYPES_AVAIL[maptype_dict_key]

    # Show information about the selected map type
    st.write(f"# {maptype.name}")
    st.write(f"{maptype.description}")

    # Show widgets if conditions defined by Selector argument `depends_on_selectors`
    # are satisfied) and get selected values
    selector_values = maptype.selector_values

    # Create map
    if st.button("Karte erstellen"):
        if selector_values.get("has_init_values", False):
            st.info("Bitte alle notwendigen Kartenattribute definieren!")
        else:
            try:
                progress_bar = st.progress(0)
                progress = 0
                with st.spinner(f"Warte auf Kartenserver ..."):
                    steps = ask_server_for_steps(maptype_dict_key)

                for step in steps:
                    with st.spinner(f"Erstelle Karte _{maptype.name}_ ({step})"):
                        step_message = send_task_to_server(
                            maptype_dict_key,
                            selector_values,
                            maptype.print_layout,
                            step,
                        )
                        progress += float(step_message["rel_weight"])
                        progress_bar.progress(progress)
                progress_bar.progress(1.0)
                st.success(f"Karte _{maptype.name}_ fertig")
                _show_download_button(step_message["filename"])

            except Exception as e:
                _show_error_message(e)

    # Show selected values for all widgets (for debugging)
    if st.checkbox("Debug"):
        st.write("## Debug Info")
        for k, v in selector_values.items():
            st.write(f"{k}: __{v}__")


def _show_download_link(filename: str):
    st.markdown(download_link(filename, "Download"), unsafe_allow_html=True)


def _show_download_button(filename: str):
    download_button_str = download_button(
        os.path.basename(filename),
        "Download",
    )
    st.markdown(download_button_str, unsafe_allow_html=True)


def _show_error_message(exception: Exception):
    st.error(f"Leider gab es einen Fehler: {exception}")
    tb = traceback.format_exc()
    st.error(tb)


def _hide_footer():
    custom_css = """
        <style>
            footer {
                visibility: hidden;
            }
        </style> """
    st.markdown(custom_css, unsafe_allow_html=True)


if __name__ == "__main__":
    start_frontend()