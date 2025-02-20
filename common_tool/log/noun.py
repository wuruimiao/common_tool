from enum import Enum, unique
import logging


@unique
class LogLevel(Enum):
    LevelNil = 0
    LevelTrace = 1
    LevelDebug = 2
    LevelInfo = 3
    LevelWarning = 4
    LevelError = 5
    LevelFatal = 6


_DefaultLevel = "info"
_DefaultFmt = "[%(asctime)s][%(levelname)s][%(filename)s:%(lineno)s][%(process)d][%(message)s]"
_DefaultTimeFmt = "%Y-%m-%d %H:%M:%S"
_DefaultFileName = "info.log"
_DefaultLogPath = "log"

LevelNames = {
    "trace": LogLevel.LevelTrace,
    "debug": LogLevel.LevelDebug,
    "info": LogLevel.LevelInfo,
    "warning": LogLevel.LevelWarning,
    "error": LogLevel.LevelError,
    "fatal": LogLevel.LevelFatal,
}

LevelToLoggingLevel = {
    LogLevel.LevelTrace: logging.DEBUG,
    LogLevel.LevelDebug: logging.DEBUG,
    LogLevel.LevelInfo: logging.INFO,
    LogLevel.LevelWarning: logging.WARNING,
    LogLevel.LevelError: logging.ERROR,
    LogLevel.LevelFatal: logging.CRITICAL,
}
