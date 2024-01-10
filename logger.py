import logging

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)-15s NevosoftPlugin %(levelname)7s: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

def set_debug(value: bool):
    if value:
        logger.setLevel(logging.DEBUG)
        stream_handler.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        stream_handler.setLevel(logging.INFO)

    logger.info("Debug mode is %s", "enabled" if value else "disabled")