from copy import copy
from typing import Iterable

import zmq

import conf_server


def ask_server_for_steps(maptype_dict_key: str) -> Iterable[str]:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{conf_server.PORT}")

    socket.send_json({"init": maptype_dict_key})

    message_from_server = socket.recv_json()

    return message_from_server["steps"]


def send_task_to_server(
    maptype_dict_key: str, data: dict, print_layout: str, step: str
) -> dict:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{conf_server.PORT}")

    data = copy(data)
    data["maptype_dict_key"] = maptype_dict_key
    data["step"] = step

    if isinstance(print_layout, str):
        data["print_layout"] = print_layout
    elif isinstance(print_layout, tuple):
        assert len(print_layout) == 2
        assert isinstance(print_layout[0], str)
        assert isinstance(print_layout[1], dict)
        data["print_layout"] = print_layout[1][data[print_layout[0]]]
    else:
        raise ValueError(
            f"MapType {maptype_dict_key} argument 'print_layout' has "
            f"wrong data type. It should be Union[str, Tuple[str, "
            f"Dict[str, str]]]."
        )

    socket.send_json(data)

    message_from_server = socket.recv_json()

    return message_from_server
