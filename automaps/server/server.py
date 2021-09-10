import time
import zmq

from automaps._qgis import start_qgis
from automaps.generators.base import StepData

import automapsconf


def _get_generators():
    return {x[0]: x[1].map_generator for x in automapsconf.MAPTYPES_AVAIL.items()}


def start_server():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{automapsconf.PORT}")
    step_data = StepData({})
    try:
        while True:
            message = socket.recv_json()
            if "init" in message.keys():
                generator = _get_generators()[message["init"]](
                    message, automapsconf.BASEPATH_FILESERVER, "", step_data
                )
                steps = generator.steps
                init_message = {"steps": list(steps.keys())}
                socket.send_json(init_message)
            else:
                generator = _get_generators()[message["maptype_dict_key"]](
                    message,
                    automapsconf.BASEPATH_FILESERVER,
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
