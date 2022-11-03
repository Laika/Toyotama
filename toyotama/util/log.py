import logging

from ..terminal.style import Style

WIDTH = 8


class CustomFormatter(logging.Formatter):
    def __init__(self, colored=True):
        self.fmt = "[%(levelname)s] %(message)s"
        self.date_format = "%Y-%m-%dT%T"
        self.FORMATS = {}
        if colored:
            self.FORMATS = {
                logging.DEBUG: Style.FG_GRAY + self.fmt + Style.RESET,
                logging.INFO: Style.FG_BLUE + self.fmt + Style.RESET,
                logging.WARNING: Style.FG_YELLOW + self.fmt + Style.RESET,
                logging.ERROR: Style.FG_RED + self.fmt + Style.RESET,
                logging.CRITICAL: Style.FG_DEEPPURPLE + self.fmt + Style.RESET,
            }
        else:
            self.FORMATS = {
                logging.DEBUG: self.fmt,
                logging.INFO: self.fmt,
                logging.WARNING: self.fmt,
                logging.ERROR: self.fmt,
                logging.CRITICAL: self.fmt,
            }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, self.date_format)
        return formatter.format(record)


def get_logger(name="toyotama", loglevel="DEBUG", colored=True):
    logging._srcfile = None
    logging.logThreads = False
    logging.logProcesses = False
    logging.logMultiprocessing = False

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    loglevel = getattr(logging, loglevel.upper(), logging.INFO)
    logger.setLevel(loglevel)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter(colored=colored))
    logger.addHandler(handler)

    return logger
