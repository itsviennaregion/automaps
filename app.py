import os

import streamlit as st

from automaps.fileserver import download_button
from conf import MAPTYPES_AVAIL
import conf_local


def start_frontend():
    maptype = MAPTYPES_AVAIL[st.sidebar.radio("Kartentyp", list(MAPTYPES_AVAIL.keys()))]

    st.write(f"# {maptype.name}")
    st.write(f"{maptype.description}")

    selector_values = {}
    for s in maptype.selectors:
        selector_values[s.label] = s.widget

    for k, v in selector_values.items():
        st.write(f"{k}: __{v}__")

    if st.button("Karte erstellen"):
        filename = maptype.generator(
            data=selector_values, basepath_fileserver=conf_local.BASEPATH_FILESERVER
        ).generate()

        with open(filename, "rb") as f:
            s = f.read()
        download_button_str = download_button(
            s, os.path.basename(filename), f"Download {os.path.basename(filename)}"
        )
        st.markdown(download_button_str, unsafe_allow_html=True)


if __name__ == "__main__":
    start_frontend()
