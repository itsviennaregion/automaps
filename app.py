import os

import streamlit as st

from automaps.fileserver import download_button
from automaps.client.client import ask_server_for_steps, send_task_to_server

from conf import MAPTYPES_AVAIL


def start_frontend():
    maptype_dict_key = st.sidebar.radio("Kartentyp", list(MAPTYPES_AVAIL.keys()))
    maptype = MAPTYPES_AVAIL[maptype_dict_key]

    st.write(f"# {maptype.name}")
    st.write(f"{maptype.description}")

    selector_values = {}
    for s in maptype.selectors:
        selector_values[s.label] = s.widget

    for k, v in selector_values.items():
        st.write(f"{k}: __{v}__")

    if st.button("Karte erstellen"):
        progress_bar = st.progress(0)
        progress = 0

        steps = ask_server_for_steps(maptype_dict_key)

        for step in steps:
            with st.spinner(f"Erstelle Karte _{maptype.name}_ ({step})"):
                step_message = send_task_to_server(
                    maptype_dict_key, selector_values, maptype.print_layout, step
                )
                progress += float(step_message["rel_weight"])
                progress_bar.progress(progress)
        progress_bar.progress(1.0)
        st.success(f"Karte _{maptype.name}_ fertig")

        filename = step_message["filename"]
        with open(filename, "rb") as f:
            s = f.read()
        download_button_str = download_button(
            s, os.path.basename(filename), f"Download {os.path.basename(filename)}"
        )
        st.markdown(download_button_str, unsafe_allow_html=True)


if __name__ == "__main__":
    start_frontend()
