from abc import ABC, abstractmethod
from typing import Callable, List, Tuple

import streamlit as st


class MapGenerator(ABC):
    name: str
    steps: List[Tuple[str, Callable]] = []
    
    def __init__(self, data: dict):
        self.data = data
        self._set_steps()
    
    def generate(self):
        print(f"{self.name} start")
        with st.spinner(f"Erstelle Karte {self.name} {self.data} ..."):
            for name, func in self.steps:
                print(name, func)
                with st.spinner(name):
                    func()
        print(f"{self.name} fertig")
        st.success(f"{self.name} fertig")
    
    @abstractmethod
    def _set_steps(self):
        pass
        

    


