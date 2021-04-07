from abc import ABC, abstractmethod
import time

import streamlit as st


class MapGenerator(ABC):
    name: str

    def generate(self):
        print(f"{self.name} start")
        with st.spinner("Karte wird erzeugt ..."):
            self._run_qgis()
        print(f"{self.name} fertig")
        st.success(f"{self.name} fertig")

    @abstractmethod
    def _run_qgis(self):
        pass
