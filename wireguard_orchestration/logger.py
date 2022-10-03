import logging


LOGGER_NAME = "WireGuardOrchestrationService"
LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"


def _get_stream_handler() -> logging.StreamHandler:
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    return stream_handler


def initialize_logger():
    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    stream_handler = _get_stream_handler()
    logger.addHandler(stream_handler)


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)
