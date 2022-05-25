from collections import OrderedDict
from logging import Logger
from pathlib import Path
import re
import threading
from typing import Union

import pytest
import zmq
from automaps.messaging.registry import Registry
from automaps.messaging.worker import State

import automapsconf


@pytest.fixture(scope="module")
def registry():
    automapsconf.PORT_REGISTRY = 96296
    r = Registry()
    threading.Thread(target=r.listen, daemon=True).start()


def send_message_to_registry(message: dict):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{automapsconf.PORT_REGISTRY}")
    if isinstance(message, dict):
        socket.send_json(message)
        return socket.recv_json()


def test_init():
    automapsconf.PORT_REGISTRY = 69269
    r = Registry()
    assert r
    assert isinstance(r.logger, Logger)
    assert isinstance(r.context, zmq.Context)
    assert isinstance(r.socket, zmq.Socket)
    assert isinstance(r._workers, dict)
    assert len(r._workers) == 0
    assert isinstance(r.workers, dict)
    assert len(r.workers) == 0
    assert isinstance(r.idle_workers, dict)
    assert len(r.idle_workers) == 0
    assert isinstance(r.idle_worker, type(None))
    assert isinstance(r.worker_states_short, dict)
    assert len(r.worker_states_short) == 0


def test_message_malformed(registry):
    message_recv = send_message_to_registry({"nonsense": 123})
    assert message_recv == {"error": "Malformed message!"}


def test_command_unkown(registry):
    message_recv = send_message_to_registry({"command": "unknown"})
    assert message_recv == {"error": "Unknown command!"}


def test_command_get_idle_worker(registry):
    message_recv = send_message_to_registry(
        {"command": "get_idle_worker", "frontend_uuid": "abc-123"}
    )
    assert message_recv == {"idle_worker_port": None}

    message_recv = send_message_to_registry({"command": "get_idle_worker"})
    assert message_recv == {"error": "Malformed message!"}


def test_command_update_state(registry):
    message_recv = send_message_to_registry(
        {
            "command": "update_state",
            "worker_uuid": "def-456",
            "server_port": 123456,
        }
    )
    assert message_recv == {"error": "Malformed message!"}

    message_recv = send_message_to_registry(
        {
            "command": "update_state",
            "worker_uuid": "def-456",
            "server_port": 123456,
            "state": str(State.IDLE),
        }
    )
    assert list(message_recv.keys()) == ["def-456"]
    assert re.match(
        r"Worker\(uuid='def-456', port=123456, state='State.IDLE', last_update='\d{4}-\d{2}-\d{2}T.*\+\d{2}:\d{2}'\)",
        message_recv["def-456"],
    )


def test_workflow_get_idle_worker(registry):
    message_recv = send_message_to_registry(
        {"command": "get_idle_worker", "frontend_uuid": "abc-123"}
    )
    assert message_recv == {"idle_worker_uuid": "def-456", "idle_worker_port": 123456}


def test_workflow_change_state_to_processing(registry):
    send_message_to_registry(
        {
            "command": "update_state",
            "worker_uuid": "def-456",
            "server_port": 123456,
            "state": str(State.PROCESSING),
        }
    )
    message_recv = send_message_to_registry(
        {"command": "get_idle_worker", "frontend_uuid": "abc-123"}
    )
    assert message_recv == {"idle_worker_port": None}


def test_workflow_add_new_idle_worker(registry):
    send_message_to_registry(
        {
            "command": "update_state",
            "worker_uuid": "ghi-789",
            "server_port": 654321,
            "state": str(State.IDLE),
        }
    )
    message_recv = send_message_to_registry(
        {"command": "get_idle_worker", "frontend_uuid": "abc-123"}
    )
    assert message_recv == {"idle_worker_uuid": "ghi-789", "idle_worker_port": 654321}


def test_workflow_shutdown_first_worker(registry):
    message_recv = send_message_to_registry(
        {
            "command": "update_state",
            "worker_uuid": "def-456",
            "server_port": 123456,
            "state": str(State.SHUTDOWN),
        }
    )
    assert re.match(
        r"Worker\(uuid='ghi-789', port=654321, state='State.IDLE', last_update='\d{4}-\d{2}-\d{2}T.*\+\d{2}:\d{2}'\)",
        message_recv["ghi-789"],
    )


def test_workflow_shutdown_second_worker(registry):
    message_recv = send_message_to_registry(
        {
            "command": "update_state",
            "worker_uuid": "ghi-789",
            "server_port": 654321,
            "state": str(State.SHUTDOWN),
        }
    )
    assert message_recv == {}
    message_recv = send_message_to_registry(
        {"command": "get_idle_worker", "frontend_uuid": "abc-123"}
    )
    assert message_recv == {"idle_worker_port": None}
