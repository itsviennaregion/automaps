import os
import subprocess
import sys
from typing import Optional


class AutoMaps:
    def __init__(self, conf_path: Optional[str] = None):
        if not conf_path:
            conf_path = os.path.dirname(os.path.join(os.getcwd(), os.path.realpath(sys.argv[-1])))
        else:
            if os.path.isabs(conf_path):
                conf_path = os.path.dirname(conf_path)
            else:
                conf_path = os.path.realpath(os.path.dirname(os.path.join(os.getcwd(), os.path.dirname(sys.argv[-1]), conf_path)))
        os.chdir(conf_path)
        automaps_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        automaps_run_path = os.path.join(automaps_path, "automaps")
        frontend = subprocess.Popen(
            [
                "streamlit",
                "run",
                os.path.join(automaps_run_path, "start_frontend.py"),
                "--",
                conf_path,
                automaps_path,
            ]
        )
        backend = subprocess.Popen(
            [
                sys.executable,
                os.path.join(automaps_run_path, "start_qgis_server.py"),
                conf_path,
                automaps_path,
            ]
        )
        try:
            frontend_stdout, frontend_stderr = frontend.communicate()
            backend_stdout, backend_stderr = backend.communicate()
        except KeyboardInterrupt:
            pass
