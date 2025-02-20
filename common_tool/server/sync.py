import contextlib
import random
from multiprocessing import Semaphore, Queue, RLock, Lock, Value
from queue import Empty
from typing import Any, Callable

from common_tool.log import logger
from common_tool.server import Context
from common_tool.system import DEFAULT_TIMEOUT


class SyncBase:
    def __init__(self):
        self._data: dict = {}

    def dict(self) -> dict:
        return {k: v for k, v in self._data.items()}

    def list(self) -> list:
        result = []
        for k, v in self._data.items():
            result.append(k)
            result.append(v)
        return result

    def init_by(self, data: dict):
        for k, v in data.items():
            self._data[k] = v

    def init_by_list(self, data: list):
        for i in range(0, len(data), 2):
            self._data[data[i]] = data[i + 1]

    def register(self, name: str, item: Any):
        if name in self._data:
            logger.error(f"SyncBase has {name}, will ignore")
            return
        self._data[name] = item

    def _get_item(self, name):
        if name not in self._data:
            logger.debug(f"SyncBase no {name}, will ignore")
            return None
            # raise Exception(f"SyncBase no {name}")
        return self._data[name]


class _SemM(SyncBase):
    """
    lock多于unlock, lock返回False
    unlock多于lock, 限制会超出limit，导致限流错误
    """
    def register(self, name: str, limit: int):
        super().register(name, Semaphore(limit))

    def lock(self, name: str) -> bool:
        return self._get_item(name).acquire(False, timeout=random.randint(1, 3))

    def unlock(self, name: str) -> bool:
        return self._get_item(name).release()


class _LockM(SyncBase):
    def register(self, name: str, item: Any):
        super().register(name, Lock())

    @contextlib.contextmanager
    def lock(self, name: str):
        self._get_item(name).acquire()
        yield
        self._get_item(name).release()


class _RLockM(SyncBase):
    def register(self, name: str, item: Any):
        super().register(name, RLock())

    @contextlib.contextmanager
    def lock_w(self, name: str):
        self._get_item(name).acquire_write()
        yield
        self._get_item(name).release()

    def lock_r(self, name: str):
        self._get_item(name).acquire_read()
        yield
        self._get_item(name).release()


class _CounterM(SyncBase):
    def register(self, name: str, item: Any = 0):
        super().register(name, (Value("i", item), Lock()))

    def get(self, name):
        return self._get_item(name)[0].value

    def set(self, name, setter: Callable):
        with self._get_item(name)[1]:
            self._get_item(name)[0].value = setter(self.get(name))
            return self.get(name)

    def increase(self, name):
        return self.set(name, lambda value: value + 1)


class _QM(SyncBase):

    def register_q(self, name: str, q: Queue):
        self.register(name, q)

    def empty_task(self):
        self._data = {name: Queue() for name in self._data.keys()}

    def add_task(self, name: str, item, timeout=DEFAULT_TIMEOUT):
        q = self._get_item(name)
        if q:
            q.put((item, Context(timeout)))

    def full(self, name: str):
        return self._get_item(name).full()

    def size(self, name: str):
        return self._get_item(name).qsize()

    def empty(self, name: str):
        return self._get_item(name).empty()

    def get_task(self, name: str, block=True) -> type[Any, Context]:
        q = self._get_item(name)
        if not q:
            return None, None

        try:
            item, ctx = q.get(block=block)
        except Empty:
            logger.debug(f"QManager get_task {name} empty")
            return None, None
        return item, ctx

    def get_a_task(self, name) -> type[Any, Context]:
        return self.get_task(name, block=False)

    def close(self):
        for name, q in self._data.items():
            q.close()
            q.join_thread()
        print("QM closed")


SemM = _SemM()
QM = _QM()
LockM = _LockM()
RLockM = _RLockM()
CounterM = _CounterM()
