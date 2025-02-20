from .noun import (
    _DefaultLevel, _DefaultFmt, _DefaultTimeFmt, _DefaultFileName, _DefaultLogPath
)


class OutputConfig(dict):
    @property
    def writer(self) -> str:
        return self.get("writer", "")

    @property
    def level(self) -> str:
        return self.get("level", _DefaultLevel)

    @property
    def format_config(self) -> dict:
        return self.get("format_config", {})

    @property
    def time_fmt(self) -> str:
        return self.format_config.get("time_fmt", _DefaultTimeFmt)

    @property
    def fmt(self) -> str:
        return self.format_config.get("fmt", _DefaultFmt)

    @property
    def writer_config(self) -> dict:
        return self.get("writer_config", {})

    @property
    def filename(self) -> str:
        return self.writer_config.get("filename", _DefaultFileName)

    @property
    def log_path(self) -> str:
        return self.writer_config.get("log_path", _DefaultLogPath)

    @property
    def max_backups(self) -> int:
        return self.writer_config.get("max_backups", 0)

    @property
    def max_age(self) -> str:
        return self.writer_config.get("max_age", "MIDNIGHT")
