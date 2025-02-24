import inspect
import os
import signal
import time
import traceback
from multiprocessing import Process
from threading import Thread
from typing import Callable, Union
import copy

from common_tool.log import logger
from common_tool.system import is_linux, cur_pid
from common_tool.call import call_async
from .sync import QM, SemM, RLockM, LockM, CounterM
from .server import init_log, init_sync


class TaskParam:
    _task_init = "_+_utils_task_init_+_"
    _task_end = "_+_utils_task_end_+_"
    _global_conf = "_+_utils_global_conf_+_"

    _sep_q = "_+_utils_sep_q_+_"
    _sep_log_q = "_+_utils_sep_log_q_+_"
    _sep_sem = "_+_utils_sem_q_+_"
    _sep_lock = "_+_utils_lock_q_+_"
    _sep_rlock = "_+_utils_rlock_q_+_"
    _sep_counter = "_+_utils_counter_+_"

    @classmethod
    def extend(cls, task) -> tuple[list, dict]:
        from common_tool.config import get_global_config
        from common_tool.log.q import QLogM

        kwargs = copy.deepcopy(task.kwargs)
        if cls._task_init in kwargs or cls._task_end in kwargs or cls._global_conf in kwargs:
            raise Exception(f"forbidden kwargs in process kwargs")
        kwargs[cls._task_init] = task.init
        kwargs[cls._task_end] = task.end
        kwargs[cls._global_conf] = get_global_config()
        # RuntimeError: Queue objects should only be shared between processes through inheritance
        # kwargs[cls._queues] = QM.dict()
        # kwargs[cls._log_q] = QLogM.log_q
        # kwargs[cls._sems] = SemM.dict()

        args = []
        args.extend(task.args)

        args.append(cls._sep_log_q)
        args.append(QLogM.log_q)

        args.append(cls._sep_q)
        args.extend(QM.list())

        args.append(cls._sep_sem)
        args.extend(SemM.list())

        args.append(cls._sep_lock)
        args.extend(LockM.list())

        args.append(cls._sep_rlock)
        args.extend(RLockM.list())

        args.append(cls._sep_counter)
        args.extend(CounterM.list())

        logger.debug(f"{args} {kwargs}")
        return args, kwargs

    @classmethod
    def _parse_args_sep(cls, sep, part):
        want = []
        if sep in part:
            ind = part.index(sep)
            want = part[ind + 1:]
            part = part[:ind]
        return want, part

    @classmethod
    def parse(cls, args, kwargs):
        init = kwargs.pop(cls._task_init, None)
        end = kwargs.pop(cls._task_end, None)
        global_conf = kwargs.pop(cls._global_conf, None)

        # log_q = kwargs.pop(cls._log_q, None)
        # queues = kwargs.pop(cls._queues, None)
        # sems = kwargs.pop(cls._sems, None)

        ind = args.index(cls._sep_log_q)
        log_q = args[ind + 1]

        sync = args[ind + 2:]
        args = args[:ind]

        # 按照append顺序倒序
        counters, sync = cls._parse_args_sep(cls._sep_counter, sync)
        rlocks, sync = cls._parse_args_sep(cls._sep_rlock, sync)
        locks, sync = cls._parse_args_sep(cls._sep_lock, sync)
        sems, sync = cls._parse_args_sep(cls._sep_sem, sync)
        qs, sync = cls._parse_args_sep(cls._sep_q, sync)

        # if cls._sep_sem in sync:
        #     ind = sync.index(cls._sep_sem)
        #     sems = sync[ind + 1:]
        #     sync = sync[:ind]

        # queues = []
        # if cls._sep_q in sync:
        #     ind = sync.index(cls._sep_q)
        #     queues = sync[ind + 1:]
        #     sync = sync[:ind]

        return args, kwargs, log_q, init, end, global_conf, qs, sems, locks, rlocks, counters


class MpDecorator:
    def __init__(self, func, grace=True):
        self.func = func
        self.grace = grace

    def __call__(self, *args, **kwargs):

        if self.grace:
            GracefulKiller(exit_now=True)

        args, kwargs, log_q, init, end, global_conf, qs, sems, locks, rlocks, counters = TaskParam.parse(args, kwargs)
        init_log(global_conf=global_conf, log_q=log_q)
        init_sync(qs, sems, locks, rlocks, counters)

        result = None
        if init:
            init()

        func_name = self.func.__name__

        try:
            if inspect.iscoroutinefunction(self.func):
                logger.debug(f"run async {func_name}")
                call_async(self.func(*args, **kwargs))
            else:
                logger.debug(f"run {func_name}")
                self.func(*args, **kwargs)
        except ErrGracefulKiller:
            print(f"{cur_pid()} {func_name} grace exit")
        except Exception as e:
            print(f"{cur_pid()} {func_name} {e}")
            msg = f"{cur_pid()} {func_name} exception {traceback.format_exc()}"
            logger.error(msg)
            from common_tool.notify import notify
            notify("mp subprocess down will restarted", msg)

        if end:
            end()
        return result


_RestartOnExitF = "restart_on_exit"


class Task:
    def __init__(self, handle, name, *args,
                 task_q_name: str = None,
                 init: Callable = None,
                 end: Callable = None,
                 **kwargs):
        self.restart_on_exit = kwargs.get(_RestartOnExitF, True)
        if _RestartOnExitF in kwargs:
            kwargs.pop(_RestartOnExitF)
        self.handle = handle
        self.args = args
        self.name = name
        self.kwargs = kwargs
        self.init = init
        self.end = end
        self.task_q_name = task_q_name
        # 进程退出自动重启


class _MultiM:
    def __init__(self):
        self._p: dict[str, Task] = {}
        self._rp: dict[int, tuple[Task, Process]] = {}
        self._t: dict[str, Task] = {}
        self._rt: dict[int, tuple[Task, Thread]] = {}
        self._killer: Union[GracefulKiller, None] = None
        self._auto_restart = False

    def auto_restart(self):
        self._auto_restart = True

    def add_p(self, name, handler, *args, **kwargs):
        if name in self._p:
            logger.debug(f"MultiM add_p {name} exist")
            return
        self._p[name] = Task(handler, name, *args, **kwargs)

    def add_once_p(self, name, handler, *args, **kwargs):
        """
        运行一次
        """
        kwargs[_RestartOnExitF] = False
        self.add_p(name, handler, *args, **kwargs)

    def add_t(self, name, handler, *args, **kwargs):
        if name in self._t:
            logger.debug(f"MultiM add_t {name} exist")
            return
        self._t[name] = Task(handler, name, *args, **kwargs)

    @property
    def close(self):
        return self._killer and self._killer.kill_now

    def _new_p(self, task: Task) -> Process:
        f = MpDecorator(task.handle, grace=True)
        args, kwargs = TaskParam.extend(task)
        p = Process(
            target=f,
            kwargs=kwargs,
            args=args,
        )
        p.start()

        self._rp[p.pid] = (task, p)

        msg = f"process {task.name} started {p.pid}"
        logger.info(msg)
        print(msg)
        return p

    def _new_t(self, task) -> Thread:
        f = task.handle
        t = Thread(
            target=f,
            name=task.name,
            kwargs=task.kwargs,
            args=task.args,
        )
        t.daemon = True
        t.start()
        self._rt[t.ident] = (task, t)

        msg = f"thread {task.name} started {t.ident}"
        logger.info(msg)
        print(msg)
        return t

    def _run_tasks(self):
        self._killer = GracefulKiller(exit_now=True, handle_child_exit=self.restart_child)
        for task in self._p.values():
            self._new_p(task)

        for task in self._t.values():
            self._new_t(task)

        msg = "server start success"
        logger.info(msg)
        print(msg)

    def _wait_p_done(self, timeout=None):
        for pid, task_p in self._rp.items():
            # print(f"process {pid} joining")
            _, p = task_p
            p.join(timeout)
            if p.is_alive():
                p.terminate()
            print(f"process {pid} joined")

    def _wait_t_done(self, timeout=None):
        for tid, task_t in self._rt.items():
            _, t = task_t
            # print(f"thread {tid} joining")
            t.join()
            print(f"thread {tid} joined")

    def _need_forever(self):
        return len(self._rp) > 0

    def start(self):
        self._run_tasks()

        msg = f"processes started in {cur_pid()}"
        print(msg)
        logger.info(msg)

        try:
            while self._need_forever():
                time.sleep(3)
            # asyncio.get_event_loop().run_forever()
        except ErrGracefulKiller:
            print()
            # print(f"will join child")

        self._wait_p_done(3)
        from common_tool.log import log
        log.close()
        self._wait_t_done()
        QM.close()

        print("MultiM start end")

    @staticmethod
    def get_exit_child_pid():
        cpid, _ = os.waitpid(-1, os.WNOHANG)
        return cpid

    def _restart_child_by_pid(self, pid):
        logger.info(f"child process-{pid} exceptionally exit")
        task_p = self._rp.get(pid)
        if not task_p:
            logger.info(f"restart child no {pid}")
            return
        task, p = task_p
        p.terminate()
        if task.restart_on_exit:
            p = self._new_p(task)
            logger.info(f"restart child {p.pid}")
        self._rp.pop(pid)

    def restart_child(self, sig, frame):
        if self.close or not self._auto_restart:
            return
        try:
            cpid = self.get_exit_child_pid()
            if cpid == 0:
                logger.error(f"no child process was immediately available")
                return
            self._restart_child_by_pid(cpid)
        except ChildProcessError:
            logger.error(f"restart child fail")


MultiM = _MultiM()


class ErrGracefulKiller(Exception):
    pass


class GracefulKiller:
    kill_now = False

    def __init__(self, exit_now=True, handle_child_exit=None):
        if not exit_now:
            handler = self._exit_gracefully
        else:
            handler = self._exit_now
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)
        if is_linux() and handle_child_exit:
            signal.signal(signal.SIGCHLD, handle_child_exit)

    def _exit_now(self, sig, frame):
        self._exit_gracefully(sig, frame)
        raise ErrGracefulKiller(f'Received signal {sig} on line {frame.f_lineno} in {frame.f_code.co_filename}')

    def _exit_gracefully(self, sig, frame):
        self.kill_now = True
