from enum import Enum
import json
import logging
import time
from uuid import uuid1
import zmq

from automaps._qgis import start_qgis
from automaps.confutils import get_config_value
from automaps.fileserver import get_streamlit_download_path
from automaps.generators.base import StepData
import automaps.logutils as lu

import automapsconf


class State(Enum):
    IDLE = 1
    INITIALIZED = 2
    PROCESSING = 3
    SHUTDOWN = 4


class QgisWorker:
    state_on_event = {
        "worker_started": State.IDLE,
        "init_job": State.INITIALIZED,
        "process_step": State.PROCESSING,
        "job_finished": State.IDLE,
        "job_cancelled": State.IDLE,
    }

    def __init__(self, worker_id: int):
        self.id = worker_id
        self.uuid = "WORKER-" + str(uuid1())
        self.port = automapsconf.PORTS_WORKERS[worker_id]

        self._uuid_short = lu.shorten_uuid(self.uuid)
        self._logger = logging.getLogger(f"worker{self.id:02d}")
        self._logger.setLevel(get_config_value("LOG_LEVEL_SERVER", logging.INFO))
        lu.add_file_handler(self._logger)

        self._task_on_event = {
            "init_job": self._init_job,
            "process_step": self._process_step,
            "job_finished": self._finish_job,
            "job_cancelled": self._cancel_job,
        }

        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.setsockopt(zmq.IDENTITY, bytes(self.uuid, "utf-8"))
        self._socket.bind(f"tcp://*:{self.port}")

        self._socket_registry = self._context.socket(zmq.REQ)
        self._socket_registry.connect(f"tcp://localhost:{automapsconf.PORT_REGISTRY}")

        self._map_type_name = None
        self._step_data = StepData({})

        self.state = self.state_on_event["worker_started"]

        self._logger.info(f"Started worker {self._uuid_short} at port {self.port}")

        self._listen()

    def __del__(self):
        self.state = State.SHUTDOWN

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, v: State):
        self._state = v
        self._logger.debug(f"State updated to {self.state}")
        self._send_state_to_registry()

    def _listen(self):
        try:
            while True:
                message = self._socket.recv_json()
                event = message["event"]
                self._task_on_event.get(event, self._unknown_message)(message)
        finally:
            self.state = State.SHUTDOWN
            self._socket.close()
            self._socket_registry.close()
            self._context.term()
            self._logger.info(
                f"Worker {self._uuid_short} on port {self.port} shutdown."
            )

    def _get_generators(self):
        return {x.name: x.map_generator for x in automapsconf.MAPTYPES_AVAIL}

    def _send_state_to_registry(self):
        message_to_registry = {
            "command": "update_state",
            "worker_id": self.id,
            "worker_uuid": self.uuid,
            "server_port": self.port,
            "state": str(self.state),
        }
        self._socket_registry.send_json(message_to_registry)
        self._socket_registry.recv_json()

    def _init_job(self, message: dict):
        self.state = self.state_on_event[message["event"]]
        self._logger.debug(f"Initializing job {lu.shorten_uuid(message['job_uuid'])}")

        self._step_data = StepData({})
        generator = self._get_generators()[message["init"]](
            message,
            str(get_streamlit_download_path()),
            "",
            self._step_data,
            message["job_uuid"],
        )
        steps = generator.steps
        init_message = {
            "worker_uuid": self.uuid,
            "server_state": str(self.state),
            "job_uuid": message["job_uuid"],
            "steps": list(steps.keys()),
        }
        self._socket.send_json(init_message)
        self._map_type_name = message["init"]

    def _process_step(self, message: dict):
        self.state = self.state_on_event[message["event"]]
        if self._map_type_name:
            data_log = {
                k: v
                for k, v in message.items()
                if "FOKUS" not in k.upper()  # TODO: move to configuration!
            }
            data_log["map_type_name"] = self._map_type_name
            self._logger.info(
                f"Beginning to process job "
                f"{lu.shorten_uuid(message['job_uuid'])}: {json.dumps(data_log)}"
            )
            self._map_type_name = None
        self._logger.debug(
            f"Processing job {lu.shorten_uuid(message['job_uuid'])}, "
            f"step '{message['step']}'"
        )
        generator = self._get_generators()[message["maptype_dict_key"]](
            message,
            str(get_streamlit_download_path()),
            message["print_layout"],
            self._step_data,
            message["job_uuid"],
        )
        self._step_data = generator.run_step(message["step"])
        step_message = self._step_data.message_to_client
        step_message["server_state"] = str(self.state)
        step_message["worker_uuid"] = self.uuid
        self._socket.send_json(step_message)

    def _finish_job(self, message: dict):
        self.state = self.state_on_event[message["event"]]
        self._step_data = StepData({})
        job_finished_message = {
            "worker_uuid": self.uuid,
            "server_state": str(self.state),
        }
        self._logger.info(f"Finished job {lu.shorten_uuid(message['job_uuid'])}")
        self._socket.send_json(job_finished_message)

    def _cancel_job(self, message: dict):
        if self.state != State.IDLE:
            self.state = self.state_on_event[message["event"]]
            self._step_data = StepData({})
            self._logger.debug(f"Cancelled job {lu.shorten_uuid(message['job_uuid'])}")
        else:
            self._logger.debug(
                f"Tried to cancel job {lu.shorten_uuid(message['job_uuid'])}, but "
                f"worker is already idle."
            )
        job_cancelled_message = {
            "worker_uuid": self.uuid,
            "server_state": str(self.state),
        }
        self._socket.send_json(job_cancelled_message)

    def _unknown_message(self, message: dict):
        unknown_event_message = {
            "worker_uuid": self.uuid,
            "error": f"Unknown Event: {message['event']}",
            "server_state": str(self.state),
        }
        self._socket.send_json(unknown_event_message)
