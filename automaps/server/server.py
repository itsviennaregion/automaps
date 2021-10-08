import logging
import time
import zmq

from automaps._qgis import start_qgis
from automaps.fileserver import get_streamlit_download_path
from automaps.generators.base import StepData
import automaps.logutils

import automapsconf


def _get_generators():
    return {x.name: x.map_generator for x in automapsconf.MAPTYPES_AVAIL}


def start_server():
    logger = logging.getLogger("server")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{automapsconf.PORT_MAP_SERVER}")
    step_data = StepData({})
    map_type_name = None
    try:
        while True:
            message = socket.recv_json()
            if "init" in message.keys():
                generator = _get_generators()[message["init"]](
                    message, str(get_streamlit_download_path()), "", step_data
                )
                steps = generator.steps
                init_message = {"steps": list(steps.keys())}
                socket.send_json(init_message)
                map_type_name = message["init"]

            else:
                if map_type_name:
                    data_log = {
                        k: v if isinstance(v, str) else v for k, v in message.items()
                    }
                    data_log["map_type_name"] = map_type_name
                    logger.debug(data_log)
                    map_type_name = None
                generator = _get_generators()[message["maptype_dict_key"]](
                    message,
                    str(get_streamlit_download_path()),
                    message["print_layout"],
                    step_data,
                )
                step_data = generator.run_step(message["step"])
                step_message = step_data.message_to_client
                socket.send_json(step_message)
    except KeyboardInterrupt:
        pass
    finally:
        socket.close()
        context.term()


if __name__ == "__main__":
    start_server()
