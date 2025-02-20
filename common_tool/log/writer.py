import logging
import os.path
from logging.handlers import TimedRotatingFileHandler

from .conf import OutputConfig
from .noun import LevelNames, LevelToLoggingLevel
from common_tool.config import get_running_conf


class BaseWriter:
    def __init__(self, conf: OutputConfig):
        self.name = "Base"
        self.output_config = conf
        self.level = LevelToLoggingLevel.get(LevelNames[conf.level], None)
        self.format_str = logging.Formatter(fmt=conf.fmt, datefmt=conf.time_fmt)
        self.handler = None


class ConsoleWriter(BaseWriter):
    def __init__(self, conf: OutputConfig):
        super().__init__(conf)
        self.name = "Console"
        self.handler = logging.StreamHandler()
        self.handler.setLevel(self.level)
        self.handler.name = self.name
        self.handler.setFormatter(self.format_str)


class FileWriter(BaseWriter):
    # 实例化TimedRotatingFileHandler
    # interval是时间间隔，backupCount是备份文件的个数，如果超过这个个数，就会自动删除，when是间隔的时间单位，单位有以下几种：
    # S 秒
    # M 分
    # H 小时
    # D 天
    # W 每星期（interval==0时代表星期一）
    # midnight 每天凌晨
    def __init__(self, conf: OutputConfig):
        super().__init__(conf)
        self.name = "File"
        filename = f"{get_running_conf().log_f_prefix}{conf.filename}"
        self.handler = TimedRotatingFileHandler(
            filename=os.path.join(conf.log_path, filename),
            when=conf.max_age, interval=1,
            backupCount=conf.max_backups, encoding="utf-8",
            # dont open log now
            delay=True,
        )
        self.handler.setLevel(self.level)
        self.handler.name = self.name
        self.handler.setFormatter(self.format_str)
