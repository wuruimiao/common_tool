import logging
import sys
import os.path
from abc import ABCMeta
from typing import List

from .conf import OutputConfig
from .mp_handler import MultiProcessingHandler
from .noun import LogLevel, _DefaultFileName, LevelToLoggingLevel
from .writer import BaseWriter, ConsoleWriter, FileWriter

from common_tool.errno import Error, OK


class BaseLogger(metaclass=ABCMeta):
    def __init__(self, writers: List[BaseWriter]):
        self.filename = ""
        self.writers = writers
        self.min_level = None

    def debug(self, format_str: str, *args, **kwargs):
        pass

    def info(self, format_str: str, *args, **kwargs):
        pass

    def warning(self, format_str: str, *args, **kwargs):
        pass

    def error(self, format_str: str, *args, **kwargs):
        pass

    def fatal(self, format_str: str, *args, **kwargs):
        pass

    def set_level(self, level: LogLevel):
        pass

    def with_fields(self, **kwargs):
        pass


class LoggingLogger(BaseLogger):
    def __init__(self, writers: List[BaseWriter]):
        # set default filename and level
        super().__init__(writers)
        self.filename = _DefaultFileName

        min_level = logging.ERROR
        set_level = False
        for writer in writers:
            if hasattr(writer, "filename"):
                self.filename = writer.filename
            if writer.level:
                set_level = True
                min_level = writer.level if writer.level < min_level else min_level

        self.logger = logging.getLogger(self.filename)
        self.logger.propagate = False
        if set_level:
            self.logger.setLevel(min_level)
            self.min_level = min_level
        else:
            self.min_level = logging.DEBUG
            self.logger.setLevel(logging.DEBUG)

        self.logger.handlers = []
        for writer in writers:
            self.logger.addHandler(MultiProcessingHandler(f"mp-handler-{writer.name}", writer.handler))

        self.logger.makeRecord = make_record

    def close(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            self.logger.removeHandler(handler)
            handler.close()

    def set_level(self, level: LogLevel):
        self.logger.setLevel(LevelToLoggingLevel.get(level))

    def trace(self, format_str: str, *args, **kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        if 'filename' not in kwargs['extra']:
            kwargs['extra']['filename'] = os.path.split(sys._getframe(1).f_code.co_filename)[1]
        if 'lineno' not in kwargs['extra']:
            kwargs['extra']['lineno'] = sys._getframe(1).f_lineno

        self.logger.debug(format_str, *args, **kwargs)

    def debug(self, format_str: str, *args, **kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        if 'filename' not in kwargs['extra']:
            kwargs['extra']['filename'] = os.path.split(sys._getframe(1).f_code.co_filename)[1]
        if 'lineno' not in kwargs['extra']:
            kwargs['extra']['lineno'] = sys._getframe(1).f_lineno

        self.logger.debug(format_str, *args, **kwargs)

    def info(self, format_str: str, *args, **kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        if 'filename' not in kwargs['extra']:
            kwargs['extra']['filename'] = os.path.split(sys._getframe(1).f_code.co_filename)[1]
        if 'lineno' not in kwargs['extra']:
            kwargs['extra']['lineno'] = sys._getframe(1).f_lineno

        self.logger.info(format_str, *args, **kwargs)

    def warning(self, format_str: str, *args, **kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        if 'filename' not in kwargs['extra']:
            kwargs['extra']['filename'] = os.path.split(sys._getframe(1).f_code.co_filename)[1]
        if 'lineno' not in kwargs['extra']:
            kwargs['extra']['lineno'] = sys._getframe(1).f_lineno

        self.logger.warning(format_str, *args, **kwargs)

    def error(self, format_str: str, *args, **kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        if 'filename' not in kwargs['extra']:
            kwargs['extra']['filename'] = os.path.split(sys._getframe(1).f_code.co_filename)[1]
        if 'lineno' not in kwargs['extra']:
            kwargs['extra']['lineno'] = sys._getframe(1).f_lineno

        self.logger.error(format_str, *args, **kwargs)

    def fatal(self, format_str: str, *args, **kwargs):
        if 'extra' not in kwargs:
            kwargs['extra'] = {}
        if 'filename' not in kwargs['extra']:
            kwargs['extra']['filename'] = os.path.split(sys._getframe(1).f_code.co_filename)[1]
        if 'lineno' not in kwargs['extra']:
            kwargs['extra']['lineno'] = sys._getframe(1).f_lineno

        self.logger.fatal(format_str, *args, **kwargs)


# overwrite logging makeRecord
def make_record(name, level, fn, lno, msg, args, exc_info,
                func=None, extra=None, sinfo=None):
    """
    A factory method which can be overridden in subclasses to create
    specialized LogRecords.
    """
    rv = logging._logRecordFactory(name, level, fn, lno, msg, args, exc_info, func,
                                   sinfo)
    if extra is not None:
        for key in extra:
            rv.__dict__[key] = extra[key]
    return rv


_Writer = {
    "console": ConsoleWriter,
    "file": FileWriter,
}

_Logger: LoggingLogger


def init(log_conf: list[dict]) -> Error:
    output_config = [OutputConfig(item) for item in log_conf]
    global _Logger
    writers = []
    for conf in output_config:
        cls = _Writer.get(conf.writer)
        if not cls:
            print(f"init_log find no {conf.writer}, optional {_Writer.keys()}")
            continue
        writers.append(cls(conf))
    if len(writers) == 0:
        writers.append(ConsoleWriter(OutputConfig()))
    _Logger = LoggingLogger(writers)
    return OK


def close():
    _Logger.close()
    from .q import QLogM
    QLogM.close()
    print("Logger closed")
