import contextlib
import logging
import bpy
from .constants import PACKAGE_NAME

formatter = logging.Formatter('%(asctime)-15s NevosoftPlugin %(levelname)7s: %(message)s')
logger = logging.getLogger(PACKAGE_NAME)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

class OperatorLogger(logging.Handler):
    """Custom logs handler to send log messages to Blender operator output."""

    def __init__(self, operator: bpy.types.Operator, level):
        super().__init__(level)
        self.operator = operator

    def emit(self, log_record):
        log_level = log_record.levelname
        log_message = self.format(log_record)

        if log_level == "CRITICAL":
            log_level = "ERROR"

        if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            log_message = "[%s] %s" % (log_level, log_message)
            log_level = "ERROR"

        self.operator.report({log_level}, log_message)

@contextlib.contextmanager
def operator_logger(operator: bpy.types.Operator, level = logging.WARN):
    try:
        handler = OperatorLogger(operator, level)
        logger.addHandler(handler)
        yield
    finally:
        logger.removeHandler(handler)

def set_debug(value: bool):
    if value:
        logger.setLevel(logging.DEBUG)
        stream_handler.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        stream_handler.setLevel(logging.INFO)

    logger.info("Debug mode is %s", "enabled" if value else "disabled")