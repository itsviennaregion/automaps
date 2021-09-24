from copy import copy
from typing import Dict, Iterable, Tuple, Union

import zmq

import automapsconf


def ask_server_for_steps(maptype_dict_key: str) -> Iterable[str]:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{automapsconf.PORT_MAP_SERVER}")

    socket.send_json({"init": maptype_dict_key})

    message_from_server = socket.recv_json()

    return message_from_server["steps"]


def send_task_to_server(
    maptype_dict_key: str,
    data: dict,
    print_layout: Union[str, Tuple[str, Dict[str, str]]],
    step: str,
) -> dict:
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{automapsconf.PORT_MAP_SERVER}")

    data = copy(data)
    data["maptype_dict_key"] = maptype_dict_key
    data["step"] = step

    if isinstance(print_layout, str):
        data["print_layout"] = print_layout
    elif isinstance(print_layout, tuple) or isinstance(print_layout, list):
        print_layout = tuple(print_layout)  # type: ignore
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
