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


def _get_generators():
    return {x.name: x.map_generator for x in automapsconf.MAPTYPES_AVAIL}


def start_server():
    logger = logging.getLogger("server")
    server_uuid = "SERVER-" + str(uuid1())
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.setsockopt(zmq.IDENTITY, bytes(server_uuid, "utf-8"))
    socket.bind(f"tcp://*:{automapsconf.PORT_MAP_SERVER}")
    map_type_name = None
    state = SERVER_STATE_ON_EVENT["start_server"]
    logger.info(f"Started Server {server_uuid} at port {automapsconf.PORT_MAP_SERVER}")
    try:
        while True:
            message = socket.recv_json()

            if message["event"] == "init_job":
                state = SERVER_STATE_ON_EVENT[message["event"]]
                step_data = StepData({})
                generator = _get_generators()[message["init"]](
                    message,
                    str(get_streamlit_download_path()),
                    "",
                    step_data,
                    message["job_uuid"],
                )
                steps = generator.steps
                init_message = {
                    "server_uuid": server_uuid,
                    "server_state": str(state),
                    "job_uuid": message["job_uuid"],
                    "steps": list(steps.keys()),
                }
                socket.send_json(init_message)
                map_type_name = message["init"]

            elif message["event"] == "process_step":
                state = SERVER_STATE_ON_EVENT[message["event"]]
                if map_type_name:
                    data_log = {
                        k: v
                        for k, v in message.items()
                        if "FOKUS" not in k.upper()  # TODO: move to configuration!
                    }
                    data_log["map_type_name"] = map_type_name
                    logger.debug(json.dumps(data_log))
                    map_type_name = None
                generator = _get_generators()[message["maptype_dict_key"]](
                    message,
                    str(get_streamlit_download_path()),
                    message["print_layout"],
                    step_data,
                    message["job_uuid"],
                )
                step_data = generator.run_step(message["step"])
                step_message = step_data.message_to_client
                step_message["server_state"] = str(state)
                step_message["server_uuid"] = server_uuid
                socket.send_json(step_message)

            elif message["event"] == "job_finished":
                state = SERVER_STATE_ON_EVENT[message["event"]]
                job_finished_message = {
                    "server_uuid": server_uuid,
                    "server_state": str(state),
                }
                socket.send_json(job_finished_message)

            else:
                unknown_event_message = {
                    "server_uuid": server_uuid,
                    "error": f"Unknown Event: {message['event']}",
                    "server_state": str(state),
                }
                socket.send_json(unknown_event_message)
    except KeyboardInterrupt:
        pass
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    start_server()
