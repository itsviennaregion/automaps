from abc import ABC, abstractmethod
from collections import namedtuple
from copy import copy
import os
from typing import Any, OrderedDict

from qgis.core import QgsPrintLayout, QgsProject

from automaps._qgis.export import export_layout
from automaps._qgis.layout import get_layout_by_name
from automaps._qgis.project import get_project, set_project_variable


Step = namedtuple("Step", "func weight")


class StepData:
    def __init__(self, message: dict):
        self.message_to_client = message


class MapGenerator(ABC):
    name: str
    steps: OrderedDict[str, Step]

    def __init__(
        self,
        data: dict,
        basepath_fileserver: str,
        print_layout: str,
        step_data: StepData,
    ):
        self.data = data
        self.basepath_fileserver = basepath_fileserver
        self.print_layout = print_layout
        self.step_data = step_data
        self.step_data.message_to_client["filename"] = self.filename

        self._set_steps()
        self.total_weight: float = sum([s.weight for s in self.steps.values()])

    @property
    def filename(self) -> str:
        data = copy(self.data)
        data.pop("maptype_dict_key", None)
        data.pop("step", None)
        data.pop("print_layout", None)
        return os.path.join(
            self.basepath_fileserver,
            f"{self.name}_{'_'.join(str(x) for x in data.values())}.pdf",
        )

    @abstractmethod
    def _set_steps(self):
        pass

    def run_step(self, name: str) -> StepData:
        self.steps[name].func()
        self.step_data.message_to_client["rel_weight"] = (
            self.steps[name].weight / self.total_weight
        )
        return self.step_data

    def _get_project(self) -> QgsProject:
        return get_project()

    def _set_project_variable(self, project: QgsProject, var_name: str, var_value: Any):
        set_project_variable(project, var_name, var_value)

    def _get_print_layout(self, project: QgsProject) -> QgsPrintLayout:
        return get_layout_by_name(project, self.print_layout)

    def _export_print_layout(self, layout: QgsPrintLayout):
        return export_layout(layout, self.filename)
