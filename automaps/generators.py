from abc import ABC, abstractmethod
import os
from typing import Callable, List, Tuple

import streamlit as st


class MapGenerator(ABC):
    name: str
    steps: List[Tuple[str, Callable]] = []

    def __init__(self, data: dict, basepath_fileserver: str):
        self.data = data
        self.basepath_fileserver = basepath_fileserver
        self._set_steps()

    def generate(self) -> str:
        with st.spinner(f"Erstelle Karte {self.name} {self.data} ..."):
            for name, func in self.steps:
                with st.spinner(name):
                    func()
        st.success(f"{self.name} fertig")
        return self.filename

    @property
    def filename(self):
        return os.path.join(
            self.basepath_fileserver, f"{self.name}_{'_'.join(self.data.values())}.txt"
        )

    @abstractmethod
    def _set_steps(self):
        pass
