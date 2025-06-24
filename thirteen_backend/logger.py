import logging
import os
from thirteen_backend.config import ENV


if ENV == "test":
    LOGGER = logging.getLogger()
else:
    CONFIG_PATH = os.path.abspath(os.path.dirname(__file__)) + "/../logging.conf"
    logging.config.fileConfig(CONFIG_PATH, disable_existing_loggers=False)

    LOGGER = logging.getLogger("appLogger")
    LOGGER.setLevel(logging.INFO)
