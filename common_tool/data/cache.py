from abc import ABC, abstractmethod
from typing import Any
from threading import Lock


# TODO: 增加时间淘汰

class Cache(ABC):
    """
    大多数基础类型赋值操作都是线程安全的，本类主要是为了防止并发重复加载
    """

    def __init__(self):
        self._lock = Lock()
        self._inited = False

    @abstractmethod
    def _load(self):
        """
        从配置中加载数据项
        :return:
        """
        pass

    def _get(self, key: str):
        return getattr(self, key, None)

    def _init_data(self):
        if self._inited:
            return
        with self._lock:
            if self._inited:
                return
            self._load()
            self._print()
            self._inited = True

    def get(self, key: str):
        self._init_data()
        return self._get(key)

    def __str__(self) -> str:
        _d = self.__dict__
        return {k: v for k, v in _d.items() if k != "_lock"}.__str__()

    def _print(self):
        from common_tool.system import cur_pid, cur_tid
        from common_tool.log import logger
        s = f"{self.__class__.__name__} in {cur_pid()} {cur_tid()} data={self}"
        logger.debug(s)


class CacheKey(ABC):
    """
    本类在key加载时加锁，保证每条key数据的一致性
    """

    def __init__(self):
        self._lock = Lock()  # 对_key_lock和_cache_data操作时加锁
        self._key_lock: dict[str, Lock] = {}  # 单key加载时加锁
        self._cache_data: dict[str, Any] = {}

    def _get_lock(self, key: str) -> Lock:
        lock = self._key_lock.get(key)
        if lock:
            return lock
        with self._lock:
            lock = self._key_lock.get(key)
            if lock:
                return lock
            lock = Lock()
            self._key_lock[key] = lock
            return lock

    def _key_inited(self, key: str):
        return key in self._cache_data

    @abstractmethod
    def _load(self, key: str):
        """
        key没有缓存时，加载数据项
        :return:
        """
        pass

    def _del(self, key: str):
        # 防止并发删除异常
        if not self._key_inited(key):
            return
        with self._lock:
            if not self._key_inited(key):
                return
            del self._cache_data[key]

    def _get(self, key: str):
        # 基础类型保证thread-safe
        return self._cache_data.get(key, None)

    def _init_data(self, key: str):
        if self._key_inited(key):
            return
        with self._get_lock(key):
            if self._key_inited(key):
                return
            r = self._load(key)
            if r is None:
                return
            self._cache_data[key] = r

    def get(self, key: str):
        self._init_data(key)
        return self._get(key)

    def del_key(self, key: str):
        return self._del(key)

    def update(self, key: str, info=None):
        """
        更新仅删除，交由get重新加载数据
        :param key:
        :param info:
        :return:
        """
        return self.del_key(key)
