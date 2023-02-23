# pylint: disable=function-redefined

"""
Utils
"""
import logging
import pickle

from src.model import Program


def serialize_program(file: str, program: Program) -> None:
    """
        Write program into object file
    """
    with open(file, 'wb') as object_file:
        pickle.dump(program, object_file, protocol=pickle.HIGHEST_PROTOCOL)


def deserialize_program(file: str) -> Program:
    """
        Read program from object file
    """
    with open(file, 'rb') as object_file:
        return pickle.load(object_file)


class CustomFormatter(logging.Formatter):

    """
        Class for customize logs
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        """
            Format log
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger() -> logging.Logger:
    """
        Generate logger
    """
    logger = logging.getLogger("Machine")
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    handler.setFormatter(CustomFormatter())

    logger.addHandler(handler)
    return logger
