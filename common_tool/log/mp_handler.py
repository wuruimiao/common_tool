import logging
from queue import Empty
from threading import Event

from .q import QLogM
"""
Note that on Windows child processes will only inherit the level of the parent process’s logger –
any other customization of the logger will not be inherited.

This is related to the lack of fork() on Windows.
Multiprocessing on Windows is implemented by launching a
new process and executing the whole Python file once again to
retrieve global variables (like your worker function).
This is called "spawning".
"""


def receive(close_event: Event, sub_handler):
    while not close_event.is_set():
        try:
            record = QLogM.receive()
            sub_handler.emit(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except (EOFError, OSError):
            break  # The queue was closed by child?
        except Empty:
            pass  # This periodically checks if the logger is closed.
        except Exception as e:
            from sys import stderr
            from traceback import print_exc

            print_exc(file=stderr)
            raise e


def _send(s):
    QLogM.log(s)


class MultiProcessingHandler(logging.Handler):
    def __init__(self, name, sub_handler):
        super().__init__()

        if sub_handler is None:
            sub_handler = logging.StreamHandler()
        self.sub_handler = sub_handler

        self.setLevel(self.sub_handler.level)
        self.setFormatter(self.sub_handler.formatter)
        self.filters = self.sub_handler.filters

        self._is_closed = Event()
        from common_tool.server import MultiM
        MultiM.add_t(name, receive, self._is_closed, self.sub_handler)

    def setFormatter(self, fmt):
        super().setFormatter(fmt)
        self.sub_handler.setFormatter(fmt)

    def _format_record(self, record):
        # ensure that exc_info and args
        # have been stringified. Removes any chance of
        # unpickleable things inside and possibly reduces
        # message size sent over the pipe.
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        try:
            s = self._format_record(record)
            _send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        if not self._is_closed.is_set():
            self._is_closed.set()
            self.sub_handler.close()
            super().close()
