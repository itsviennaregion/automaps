from copy import copy
from typing import Iterable

import zmq

import automapsconf


def ask_server_for_steps(maptype_dict_key: str) -> Iterable[str]:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{automapsconf.PORT}")

    socket.send_json({"init": maptype_dict_key})

    message_from_server = socket.recv_json()

    return message_from_server["steps"]


def send_task_to_server(
    maptype_dict_key: str, data: dict, print_layout: str, step: str
) -> dict:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{automapsconf.PORT}")

    data = copy(data)
    data["maptype_dict_key"] = maptype_dict_key
    data["step"] = step
    data["print_layout"] = print_layout

    socket.send_json(data)

    message_from_server = socket.recv_json()

    return message_from_server
