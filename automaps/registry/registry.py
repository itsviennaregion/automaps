from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import logging
from typing import Dict, List, Optional, Union
from uuid import uuid1
import zmq

import automaps.logutils
from automaps.server.server import State

import automapsconf


@dataclass
class Worker:
    uuid: str
    port: int
    state: str
    last_update: str


@dataclass
class ServerRequest:
    server_uuid: str
    command: str
    state: str


class Registry:
    def __init__(self):
        self.logger = logging.getLogger("registry")

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{automapsconf.PORT_REGISTRY}")

        self._workers: Dict[str, Worker] = {}

        self.logger.info(f"Started Registry on port {automapsconf.PORT_REGISTRY}")

    def __del__(self):
        self.socket.close()
        self.context.term()

    @property
    def workers(self):
        return {
            server_uuid: str(worker) for server_uuid, worker in self._workers.items()
        }

    @property
    def idle_workers(self) -> Dict[str, Worker]:
        return {
            server_uuid: worker
            for server_uuid, worker in self._workers.items()
            if worker.state == str(State.IDLE)
        }

    @property
    def idle_worker(self) -> Optional[Worker]:
        if len(self.idle_workers) > 0:
            return list(self.idle_workers.values())[0]
        else:
            return None

    def listen(self):
        try:
            while True:
                message = self.socket.recv_json()
                # self.logger.info(f"Registry received {message}")

                if message["command"] == "update_state":
                    self._update_state(message)

                if message["command"] == "get_idle_worker":
                    self._get_idle_worker(message)
        except KeyboardInterrupt:
            pass
        finally:
            self.socket.close()
            self.context.term()

    def _update_state(self, message: dict):
        self._workers[message["server_uuid"]] = Worker(
            message["server_uuid"],
            message["server_port"],
            message["state"],
            datetime.now(timezone.utc).isoformat(),
        )

        self.socket.send_json(self.workers)
        # self.logger.info(f"Registry sent message {self.workers}")

    def _get_idle_worker(self, message: dict):
        if self.idle_worker is not None:
            message = {"idle_worker_port": self.idle_worker.port}
        else:
            message = {"idle_worker_port": None}
        self.socket.send_json(message)
        # self.logger.info(f"Registry sent message {message}")
