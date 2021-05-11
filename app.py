import os
import traceback

import streamlit as st

from automaps.fileserver import download_button
from automaps.client.client import ask_server_for_steps, send_task_to_server
from conf import MAPTYPES_AVAIL


def start_frontend():
    st.set_page_config(page_title="VOR Karten")

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
    st.write("## Debug Info")
    for k, v in selector_values.items():
        st.write(f"{k}: __{v}__")


def _show_download_button(filename: str):
    with open(filename, "rb") as f:
        s = f.read()
    download_button_str = download_button(
        s,
        os.path.basename(filename),
        "Download",
    )
    st.markdown(download_button_str, unsafe_allow_html=True)


def _show_error_message(exception: Exception):
    st.error(f"Leider gab es einen Fehler: {exception}")
    tb = traceback.format_exc()
    st.error(tb)


if __name__ == "__main__":
    start_frontend()
