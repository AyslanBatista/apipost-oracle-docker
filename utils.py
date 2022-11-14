import logging
import os
from logging import handlers
from typing import Union

ROOT_PATH = os.path.dirname(__file__)
LOG_PATH = os.path.join(ROOT_PATH, "valor_log.log")

LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
log = logging.getLogger("api")
fmt = logging.Formatter(
    "%(asctime)s  %(name)s  %(levelname)s "
    "l:%(lineno)d f:%(filename)s: %(message)s"
)


def get_logger(
    logfile: Union[str, os.PathLike[str]] = "api.log"
) -> logging.Logger:
    """Returns a configured logger."""
    # ch = logging.StreamHandler()  # Console/terminal/stderr
    # ch.setLevel(log_level)
    fh = handlers.RotatingFileHandler(
        logfile,
        maxBytes=10**6,
        backupCount=10,
    )
    fh.setLevel(LOG_LEVEL)
    # ch.setFormatter(fmt)
    fh.setFormatter(fmt)
    # log.addHandler(ch)
    log.addHandler(fh)
    return log
