import logging

from .terminal.style import Style


class CustomFormatter(logging.Formatter):
    def __init__(self, colored=True):
        self.date_format = "%Y-%m-%dT%T"
        self.FORMATS = {}
        if colored:
            self.FORMATS = {
                logging.DEBUG: self._colored_format(Style.FG_GRAY),
                logging.INFO: self._colored_format(Style.FG_BLUE),
                logging.WARNING: self._colored_format(Style.FG_YELLOW),
                logging.ERROR: self._colored_format(Style.FG_RED),
                logging.CRITICAL: self._colored_format(Style.FG_DEEPPURPLE + Style.BOLD),
            }
        else:
            self.FORMATS = {
                logging.DEBUG: self._colored_format(),
                logging.INFO: self._colored_format(),
                logging.WARNING: self._colored_format(),
                logging.ERROR: self._colored_format(),
                logging.CRITICAL: self._colored_format(),
            }

    def _colored_format(self, color: str = "") -> str:
        return f"{Style.FG_GRAY}{{asctime}}  {color}{{levelname: <8}}  {{message}}{Style.RESET}"

    def format(self, record: logging.LogRecord):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, self.date_format, style="{")
        return formatter.format(record)


def get_logger(name: str = "toyotama", loglevel: str = "DEBUG", colored: bool = True) -> logging.Logger:
    logging._srcfile = None
    logging.logThreads = False
    logging.logProcesses = False
    logging.logMultiprocessing = False

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    loglevel = getattr(logging, loglevel.upper(), "INFO")
    logger.setLevel(loglevel)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter(colored=colored))
    logger.addHandler(handler)

    return logger
