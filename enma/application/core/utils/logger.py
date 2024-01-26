from enum import Enum
import logging
from typing import Optional

class LogMode(Enum):
    DEBUG = logging.DEBUG
    SILENT = -1
    NORMAL = logging.INFO

class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    green = "\x1b[32;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    _format = "%(name)s - [%(levelname)s]: %(message)s (%(filename)s:%(lineno)d)"

    def __init__(self, template: Optional[str] = None):
        
        if template is not None:
            self._format = template

        self.FORMATS = {
            logging.DEBUG: self.grey + self._format + self.reset,
            logging.INFO: self.green + self._format + self.reset,
            logging.WARNING: self.yellow + self._format + self.reset,
            logging.ERROR: self.red + self._format + self.reset,
            logging.CRITICAL: self.bold_red + self._format + self.reset
        }
        

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

class Logger(logging.Logger):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)
        self._mode = LogMode.SILENT
        self.create_handlers()
        
    def create_handlers(self) -> None:
        debug_formatter = CustomFormatter(template="%(asctime)s - %(name)s - [DEBUG] - %(message)s (in %(funcName)s at %(filename)s:%(lineno)d)")
        info_formatter = CustomFormatter(template="%(name)s - [%(levelname)s]: %(message)s")

        handler = logging.StreamHandler()
        handler.setFormatter(debug_formatter)

        self.addHandler(handler)

        self._debug_formatter = debug_formatter
        self._info_formatter = info_formatter

    @property
    def mode(self) -> LogMode:
        return self._mode

    @mode.setter
    def mode(self, mode: LogMode) -> None:
        if mode == LogMode.SILENT:
            self.disabled = True
            return
        
        if mode == LogMode.DEBUG:
            for handler in self.handlers:
                handler.setFormatter(self._debug_formatter)
        else:
            for handler in self.handlers:
                handler.setFormatter(self._info_formatter)
        
        self.disabled = False
        self.setLevel(mode.value)
        self._mode = mode

logger = Logger('Enma')
