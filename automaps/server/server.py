from enum import Enum
import json
import logging
import time
from uuid import uuid1
import zmq

from automaps._qgis import start_qgis
from automaps.fileserver import get_streamlit_download_path
from automaps.generators.base import StepData
import automaps.logutils

import automapsconf


class State(Enum):
    STARTED = 0
    IDLE = 1
    INITIALIZED = 2
    PROCESSING = 3


SERVER_STATE_ON_EVENT = {
    "start_server": State.IDLE,
    "init_job": State.INITIALIZED,
    "process_step": State.PROCESSING,
    "job_finished": State.IDLE,
}


class QgisWorker:
    def __init__(self, worker_id: int):
        self.logger = logging.getLogger("server")
        self.uuid = "WORKER-" + str(uuid1())

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.setsockopt(zmq.IDENTITY, bytes(self.uuid, "utf-8"))
        self.socket.bind(f"tcp://*:{automapsconf.PORTS_WORKERS[worker_id]}")
        self.port = automapsconf.PORTS_WORKERS[worker_id]

        self.socket_registry = self.context.socket(zmq.REQ)
        self.socket_registry.connect(f"tcp://localhost:{automapsconf.PORT_REGISTRY}")

        self.map_type_name = None

        self.state = SERVER_STATE_ON_EVENT["start_server"]
        self._send_state_to_registry()

        self.logger.info(f"Started worker {self.uuid} at port {self.port}")
        try:
            while True:
                message = self.socket.recv_json()

                if message["event"] == "init_job":
                    self.state = SERVER_STATE_ON_EVENT[message["event"]]
                    self._send_state_to_registry()

                    step_data = StepData({})
                    generator = self._get_generators()[message["init"]](
                        message,
                        str(get_streamlit_download_path()),
                        "",
                        step_data,
                        message["job_uuid"],
                    )
                    steps = generator.steps
                    init_message = {
                        "server_uuid": self.uuid,
                        "server_state": str(self.state),
                        "job_uuid": message["job_uuid"],
                        "steps": list(steps.keys()),
                    }
                    self.socket.send_json(init_message)
                    self.map_type_name = message["init"]

                elif message["event"] == "process_step":
                    self.state = SERVER_STATE_ON_EVENT[message["event"]]
                    self._send_state_to_registry()
                    if self.map_type_name:
                        data_log = {
                            k: v
                            for k, v in message.items()
                            if "FOKUS" not in k.upper()  # TODO: move to configuration!
                        }
                        data_log["map_type_name"] = self.map_type_name
                        self.logger.debug(json.dumps(data_log))
                        self.map_type_name = None
                    generator = self._get_generators()[message["maptype_dict_key"]](
                        message,
                        str(get_streamlit_download_path()),
                        message["print_layout"],
                        step_data,
                        message["job_uuid"],
                    )
                    step_data = generator.run_step(message["step"])
                    step_message = step_data.message_to_client
                    step_message["server_state"] = str(self.state)
                    step_message["server_uuid"] = self.uuid
                    self.socket.send_json(step_message)

                elif message["event"] == "job_finished":
                    self.state = SERVER_STATE_ON_EVENT[message["event"]]
                    self._send_state_to_registry()
                    step_data = StepData({})
                    job_finished_message = {
                        "server_uuid": self.uuid,
                        "server_state": str(self.state),
                    }
                    self.socket.send_json(job_finished_message)

                else:
                    unknown_event_message = {
                        "server_uuid": self.uuid,
                        "error": f"Unknown Event: {message['event']}",
                        "server_state": str(self.state),
                    }
                    self.socket.send_json(unknown_event_message)
        except KeyboardInterrupt:
            self.socket.close()
            self.context.term()
        finally:
            self.socket.close()
            self.context.term()

    def _get_generators(self):
        return {x.name: x.map_generator for x in automapsconf.MAPTYPES_AVAIL}

    def _send_state_to_registry(self):
        message_to_registry = {
            "server_uuid": self.uuid,
            "server_port": self.port,
            "command": "update_state",
            "state": str(self.state),
        }
        self.socket_registry.send_json(message_to_registry)
        # self.logger.info(
        #     f"Message from server {self.uuid} to registry: {message_to_registry}"
        # )
        message_from_registry = self.socket_registry.recv_json()
        # self.logger.info(
        #     f"Message from registry to server {self.uuid}: {message_from_registry}"
        # )
