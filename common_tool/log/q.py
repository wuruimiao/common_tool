from multiprocessing import Queue
from threading import Event


class _QLogM:
    def __init__(self):
        super().__init__()
        self._log_q: Queue = Queue()
        self._log_q_stop = Event()
        self.start_log()

    @property
    def log_q(self):
        return self._log_q

    def init_q(self, q: Queue):
        self._log_q = q

    def receive(self):
        return self._log_q.get(timeout=0.2)

    def log(self, s):
        self._log_q_stop.wait()
        try:
            self._log_q.put_nowait(s)
        except ValueError:
            print(f"QLogM q is closed")

    # 原来是为了暂停写日志，目前不需要
    def pause_log(self):
        self._log_q_stop.clear()

    def start_log(self):
        self._log_q_stop.set()

    def log_empty(self) -> bool:
        return self._log_q.empty()

    def close(self):
        self._log_q.close()
        self._log_q.join_thread()
        print("QLogM closed")


QLogM = _QLogM()
