import os
import subprocess
import sys


class AutoMaps:
    def __init__(self, conf_path: str):
        conf_path = os.path.dirname(os.path.abspath(conf_path))
        automaps_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        # if conf_path not in sys.path:
        # sys.path.append(os.path.dirname(conf_path))
        # if automaps_path not in sys.path:
        # sys.path.append(automaps_path)
        # print(sys.path)
        frontend = subprocess.Popen(["streamlit", "run", "./automaps/start_frontend.py", "--", conf_path, automaps_path])
        frontend_stdout, frontend_stderr = frontend.communicate()
        backend = subprocess.Popen(["python3", "start_qgis_server.py", conf_path, automaps_path])
        backend_stdout, backend_stderr = backend.communicate()