from abc import ABC, abstractmethod
from collections import namedtuple
import os
from typing import Callable, List, Tuple

import streamlit as st

Step = namedtuple("Step", "name func weight")


class MapGenerator(ABC):
    name: str
    steps: List[Step] = []

    def __init__(self, data: dict, basepath_fileserver: str):
        self.data = data
        self.basepath_fileserver = basepath_fileserver
        self._set_steps()
        self.total_weight: float = sum([s.weight for s in self.steps])

    def generate(self) -> str:
        progress_bar = st.progress(0)
        progress = 0
        for step in self.steps:
            with st.spinner(f"Erstelle Karte _{self.name}_ ({step.name})"):
                step.func()
            progress += float(step.weight / self.total_weight)
            progress_bar.progress(progress)
        st.success(f"Karte _{self.name}_ fertig")
        return self.filename

    @property
    def filename(self):
        return os.path.join(
            self.basepath_fileserver,
            f"{self.name}_{'_'.join(str(x) for x in self.data.values())}.txt",
        )

    @abstractmethod
    def _set_steps(self):
        pass
