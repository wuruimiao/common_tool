import json
import os.path
import sys
import traceback

from .log import LoggingLogger
from common_tool.log import log


# _Logger: LoggingLogger


def ensure_filepath_and_lineno(**kwargs):
    if 'extra' not in kwargs:
        kwargs['extra'] = {}
    if 'filename' not in kwargs['extra']:
        kwargs['extra']['filename'] = os.path.split(sys._getframe(2).f_code.co_filename)[1]
    if 'lineno' not in kwargs['extra']:
        kwargs['extra']['lineno'] = sys._getframe(2).f_lineno
    return kwargs


def debug(format_str: str, *args, **kwargs):
    try:
        kwargs = ensure_filepath_and_lineno(**kwargs)
        _Logger: LoggingLogger = getattr(log, "_Logger", None)
        if _Logger:
            _Logger.debug(format_str, *args, **kwargs)
        else:
            print("debug: ", format_str % args)
    except Exception as err:  # pylint: disable=broad-except
        print(f"log err! format_str: {format_str}; "
              f"args: {json.dumps(args)}; "
              f"err: {repr(err)}"
              f"\n{traceback.format_exc()}")


def info(format_str: str, *args, **kwargs):
    try:
        kwargs = ensure_filepath_and_lineno(**kwargs)
        _Logger: LoggingLogger = getattr(log, "_Logger", None)
        if _Logger:
            _Logger.info(format_str, *args, **kwargs)
        else:
            print("info: ", format_str % args)
    except Exception as err:  # pylint: disable=broad-except
        print(f"log err! format_str: {format_str}; "
              f"args: {json.dumps(args)}; "
              f"err: {repr(err)}"
              f"\n{traceback.format_exc()}")


def warning(format_str: str, *args, **kwargs):
    try:
        kwargs = ensure_filepath_and_lineno(**kwargs)
        _Logger: LoggingLogger = getattr(log, "_Logger", None)
        if _Logger:
            _Logger.warning(format_str, *args, **kwargs)
        else:
            print("warning: ", format_str % args)
    except Exception as err:  # pylint: disable=broad-except
        print(f"log err! format_str: {format_str}; "
              f"args: {json.dumps(args)}; "
              f"err: {repr(err)}"
              f"\n{traceback.format_exc()}")


def error(format_str: str, *args, **kwargs):
    try:
        kwargs = ensure_filepath_and_lineno(**kwargs)
        _Logger: LoggingLogger = getattr(log, "_Logger", None)
        if _Logger:
            _Logger.error(format_str, *args, **kwargs)
        else:
            print("error: ", format_str % args)
    except Exception as err:  # pylint: disable=broad-except
        print(f"log err! format_str: {format_str}; "
              f"args: {json.dumps(args)}; "
              f"err: {repr(err)}"
              f"\n{traceback.format_exc()}")


def fatal(format_str: str, *args, **kwargs):
    try:
        kwargs = ensure_filepath_and_lineno(**kwargs)
        _Logger: LoggingLogger = getattr(log, "_Logger", None)
        if _Logger:
            _Logger.fatal(format_str, *args, **kwargs)
        else:
            print("fatal: ", format_str % args)
    except Exception as err:  # pylint: disable=broad-except
        print(f"log err! format_str: {format_str}; "
              f"args: {json.dumps(args)}; "
              f"err: {repr(err)}"
              f"\n{traceback.format_exc()}")
