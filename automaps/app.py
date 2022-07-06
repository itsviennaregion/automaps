import os
import subprocess
import sys
from typing import Optional


class AutoMaps:
    def __init__(self, conf_path: Optional[str] = None):
        if not conf_path:
            conf_path = os.path.dirname(
                os.path.join(os.getcwd(), os.path.realpath(sys.argv[-1]))
            )
        else:
            if os.path.isabs(conf_path):
                conf_path = os.path.dirname(conf_path)
            else:
                conf_path = os.path.realpath(
                    os.path.dirname(
                        os.path.join(
                            os.getcwd(), os.path.dirname(sys.argv[-1]), conf_path
                        )
                    )
                )
        os.chdir(conf_path)
        automaps_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        automaps_run_path = os.path.join(automaps_path, "automaps")

        if conf_path not in sys.path:
            sys.path.insert(0, conf_path)
        if automaps_path not in sys.path:
            sys.path.append(automaps_path)

        import automapsconf

        logger_server = subprocess.Popen(
            [
                sys.executable,
                os.path.join(automaps_run_path, "start_logger_server.py"),
                conf_path,
                automaps_path,
            ]
        )
        registry = subprocess.Popen(
            [
                sys.executable,
                os.path.join(automaps_run_path, "start_registry.py"),
                conf_path,
                automaps_path,
            ]
        )
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
        workers = []
        for port in automapsconf.PORTS_WORKERS:
            worker = subprocess.Popen(
                [
                    sys.executable,
                    os.path.join(automaps_run_path, "start_qgis_worker.py"),
                    conf_path,
                    automaps_path,
                    str(port),
                ]
            )
            workers.append(worker)
        try:
            _, _ = logger_server.communicate()
            _, _ = registry.communicate()
            _, _ = frontend.communicate()
            for worker in workers:
                _, _ = worker.communicate()
        except KeyboardInterrupt:
            pass
        finally:
            for worker in workers:
                worker.kill()
            frontend.kill()
            registry.kill()
            logger_server.kill
