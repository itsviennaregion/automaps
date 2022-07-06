from datetime import datetime
import logging
import logging.handlers
import signal
import sys
from typing import Optional, Union
from uuid import UUID

import zmq

from automaps.confutils import get_config_value


class LoggerClient(logging.getLoggerClass()):
    def __init__(self, name: str):
        """This subclass of logging.Logger handles log records by sending them to the
        central logger server.

        Args:
            name (str): The name of the logger.
        """
        super().__init__(name)

        self.setLevel(get_config_value("LOG_LEVEL_SERVER", logging.INFO))
        for handler in self.handlers:
            self.removeHandler(handler)

        self.port_zmq = get_config_value("PORT_LOGGER_SERVER", 62855)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REQ)
        self._socket.connect(f"tcp://localhost:{self.port_zmq}")

    def handle(self, record: logging.LogRecord):
        self._socket.send_pyobj(record)
        self._socket.recv_string()


class LoggerServer:
    def __init__(self):
        """This class acts as a server for collecting log records coming from other
        components and for writing them out centrally.
        """
        self.logger = logging.getLogger("logger")
        self.logger.setLevel(get_config_value("LOG_LEVEL_SERVER", logging.INFO))
        add_file_handler(self.logger)

        self.port_zmq = get_config_value("PORT_LOGGER_SERVER", 62855)
        self._context = zmq.Context()
        self._socket = self._context.socket(zmq.REP)
        self._socket.bind(f"tcp://*:{self.port_zmq}")

        signal.signal(signal.SIGTERM, self._cleanup)
        signal.signal(signal.SIGINT, self._cleanup)

        self.logger.info(f"Started Logger Server on port {self.port_zmq}")

    def listen(self):
        """Receive messages from socket and handle incoming log records."""
        while True:
            record = self._socket.recv_pyobj()
            self.logger.handle(record)
            self._socket.send_string("Done")

    def _listen_finally(self, max_seconds: int = 2):
        """Before shuting down, listen for for some time to log shutdown messages
        coming from other components.

        Args:
            max_seconds (int, optional): _description_. Defaults to 2.
        """
        self._socket.setsockopt(zmq.SNDTIMEO, 100)
        self._socket.setsockopt(zmq.RCVTIMEO, 100)
        start_time = datetime.now()
        while True:
            try:
                record = self._socket.recv_pyobj()
                self.logger.handle(record)
                self._socket.send_string("Done")
            except zmq.error.Again:
                pass
            if (datetime.now() - start_time).total_seconds() >= max_seconds:
                break

    def _cleanup(self, *args):
        """Shut down gracefully."""
        self._listen_finally()
        self._socket.close()
        self._context.term()
        self.logger.info(f"Stopped Logger Server on port {self.port_zmq}")
        sys.exit()


def add_file_handler(logger: logging.Logger) -> bool:
    if get_config_value("LOG_PATH"):
        format_logfile = get_config_value(
            "LOG_FORMAT", "%(asctime)s -- %(levelname)-7s -- %(name)s -- %(message)s"
        )
        formatter_logfile = logging.Formatter(format_logfile)
        fh = logging.handlers.TimedRotatingFileHandler(
            get_config_value("LOG_PATH"), when="W0"  # TODO: automapsconf.py
        )
        fh.setLevel(get_config_value("LOG_LEVEL_SERVER", logging.INFO))
        fh.setFormatter(formatter_logfile)
        logger.addHandler(fh)
        return True
    return False


def shorten_uuid(uuid: Union[UUID, str], extra_short: Optional[bool] = False) -> str:
    uuid = str(uuid)
    try:
        prefix = "" if extra_short else uuid.split("-")[0]
        return prefix + uuid.split("-")[1]
    except IndexError:
        return uuid
