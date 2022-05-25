from collections import OrderedDict
from logging import Logger
from pathlib import Path
import re
import threading
from typing import Union

import pytest
import zmq
from automaps.messaging.client import ask_worker_for_steps
from automaps.messaging.registry import Registry
from automaps.messaging.worker import QgisWorker, State

import automapsconf


PORTS_WORKER = [718452, 718453]


@pytest.fixture(scope="module")
def registry():
    automapsconf.PORT_REGISTRY = 15296
    r = Registry()
    threading.Thread(target=r.listen, daemon=True).start()


class ThreadedWorker(threading.Thread):
    daemon = True

    def run(self):
        self.w = QgisWorker(port=PORTS_WORKER[0])


@pytest.fixture(scope="module")
def worker():
    automapsconf.PORT_REGISTRY = 15296
    ThreadedWorker().start()


def test_init(registry, worker):
    steps = ask_worker_for_steps("maptype_1", "JOB-uuid", PORTS_WORKER[0])
    assert steps == ""
