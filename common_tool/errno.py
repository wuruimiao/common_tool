class Error(object):
    def __init__(self, code_int: int, code: str, desc: str = ""):
        self.code_int = code_int
        self.code = code
        self.desc = desc

    @property
    def ok(self):
        return self.code_int == 0

    def __str__(self):
        return f"code={self.code_int} message={self.code}:{self.desc}"

    @property
    def error(self) -> str:
        return self.desc

    def dict(self) -> dict:
        return {"code": self.code_int, "message": self.desc}


OK = Error(0, "", "")
INTERVAL_SERVER = Error(500, "Internal Server Error", "服务内部错误，请联系管理员")
TIMEOUT = Error(599, "TIMEOUT", "超时")
MISS_CONFIG = Error(1000, "ERR_MISS_CONFIG", "配置文件丢失")
BROKEN_CONFIG = Error(1001, "ERR_BROKEN_CONFIG", "配置文件损坏")
MISS_ZIP = Error(1002, "ERR_MISS_ZIP", "zip丢失")
BROKEN_ZIP = Error(1003, "ERR_BROKEN_ZIP", "zip已损坏")
BROKEN_JSON = Error(1004, "ERR_BROKEN_JSON", "json文件已损坏")
MISS_JSON = Error(1005, "ERR_MISS_JSON", "json文件丢失")
COPY_FILE = Error(1006, "ERR_COPY_FILE", "文件拷贝失败")
NO_FILE = Error(1007, "ERR_NO_FILE", "文件不存在")

COPY_FILE_EXIST = Error(1010, "ERR_COPY_FILE_EXIST", "拷贝目标文件已存在")

ASYNC_DOWNLOAD = Error(1018, "ERR_ASYNC_DOWNLOAD", "异步下载出错")

FILE_BROKEN = Error(1027, "ERR_FILE_BROKEN", "文件损坏")
