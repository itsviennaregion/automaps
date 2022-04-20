from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
from typing import Dict, List, Optional, Union
from uuid import uuid1
import signal
import streamlit
import sys
import zmq

from automaps.confutils import get_config_value
import automaps.logutils as lu
from automaps.worker.worker import State

import automapsconf


@dataclass
class Worker:
    uuid: str
    port: int
    state: str
    last_update: str


class Registry:
    def __init__(self):
        self.logger = logging.getLogger("registry")
        self.logger.setLevel(get_config_value("LOG_LEVEL_SERVER", logging.INFO))
        lu.add_file_handler(self.logger)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{automapsconf.PORT_REGISTRY}")

        self._workers: Dict[str, Worker] = {}

        self.logger.info(f"Started Registry on port {automapsconf.PORT_REGISTRY}")

        signal.signal(signal.SIGTERM, self._cleanup)
        signal.signal(signal.SIGINT, self._cleanup)

    def _cleanup(self, *args):
        self.socket.close()
        self.context.term()
        self.logger.info(f"Stopped Registry on port {automapsconf.PORT_REGISTRY}")
        sys.exit()

    @property
    def workers(self):
        return {
            worker_uuid: str(worker) for worker_uuid, worker in self._workers.items()
        }

    @property
    def idle_workers(self) -> Dict[str, Worker]:
        return {
            worker_uuid: worker
            for worker_uuid, worker in self._workers.items()
            if worker.state == str(State.IDLE)
        }

    @property
    def idle_worker(self) -> Optional[Worker]:
        if len(self.idle_workers) > 0:
            return list(self.idle_workers.values())[0]
        else:
            return None

    @property
    def worker_states_short(self) -> Dict[str, str]:
        return {lu.shorten_uuid(k): v.state for k, v in self._workers.items()}

    def listen(self):
        while True:
            message = self.socket.recv_json()
            self.logger.debug(f"Registry received {message}")

            if message["command"] == "update_state":
                self._update_state(message)

            if message["command"] == "get_idle_worker":
                self._get_idle_worker(message)

    def _update_state(self, message: dict):
        if message["worker_uuid"] not in self._workers.keys():
            self.logger.info(
                f"New worker {lu.shorten_uuid(message['worker_uuid'])} registered."
            )
        self._workers[message["worker_uuid"]] = Worker(
            message["worker_uuid"],
            message["server_port"],
            message["state"],
            datetime.now(timezone.utc).isoformat(),
        )
        if message["state"] == str(State.SHUTDOWN):
            del self._workers[message["worker_uuid"]]
            self.logger.info(
                f"Worker {lu.shorten_uuid(message['worker_uuid'])} was shut down and "
                f"has been deregistered."
            )
        self.socket.send_json(self.workers)
        self.logger.debug(
            f"State updated: worker "
            f"{lu.shorten_uuid(message['worker_uuid'])} -> {message['state']}. "
            f"States are now: {self.worker_states_short}"
        )

    def _get_idle_worker(self, message: dict):
        self.logger.debug(
            f"Frontend {lu.shorten_uuid(message['frontend_uuid'])} is asking for idle "
            f"workers. Worker states: {self.worker_states_short}"
        )
        if self.idle_worker is not None:
            return_message = {
                "idle_worker_uuid": self.idle_worker.uuid,
                "idle_worker_port": self.idle_worker.port,
            }
        else:
            return_message = {"idle_worker_port": None}
        self.logger.debug(f"Result of idle worker search: {return_message}")
        self.socket.send_json(return_message)
