import os
import random
import socket
import subprocess
import threading
import time
from importlib import import_module
import multiprocessing

from common_tool.errno import Error, OK, TIMEOUT, INTERVAL_SERVER
from common_tool.log import logger

from .plat import is_win, is_linux

# 秒数
DEFAULT_TIMEOUT = 30 * 60


def cur_pid() -> int:
    return os.getpid()


def cur_tid() -> int:
    return threading.currentThread().ident


def get_host_ip() -> str:
    """
    查询本机ip地址
    :return: ip
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def import_by_name(name: str):
    return import_module(name)


def run_cmd(cmd: list[str], env=None, timeout=DEFAULT_TIMEOUT) -> tuple[str, bool]:
    try:
        out = subprocess.check_output(
            cmd, timeout=timeout, env=env,
            # pass arguments as a list of strings
            # shell=True,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
        )
        out = out.replace("\r\n", "\n")
        logger.info(f"{cmd} output={out}")
        return out, True
    except subprocess.CalledProcessError as e:
        out = e.output
        logger.error(f"{cmd} output={out}")
        return out, False
    except (FileNotFoundError, PermissionError) as e:
        out = f"{e}"
        logger.error(f"{cmd} output={out}")
        return out, False
    except subprocess.TimeoutExpired as e:
        out = f"{e}"
        logger.error(f"{cmd} timeout output={out}")
        return out, False


def remote_sync_files(local_folder, remote_folder, remote_host, remote_user):
    return run_cmd([
        'rsync', '-avzR', local_folder, f'{remote_user}@{remote_host}:{remote_folder}'
    ])


def remote_create_file(remote_host, remote_user, remote_file_dir):
    return run_cmd([
        'ssh', f'{remote_user}@{remote_host}', 'touch', remote_file_dir
    ])


def remote_rm_file(remote_host, remote_user, remote_file_dir):
    return run_cmd([
        'ssh', f'{remote_user}@{remote_host}', 'rm', '-rf', remote_file_dir
    ])


def remote_file_exist(remote_host, remote_user, remote_file_dir):
    output, ok = run_cmd(['ssh', f'{remote_user}@{remote_host}', 'test', '-f', remote_file_dir,
                          "&&", 'echo', 'File', 'exists', '||', 'echo', "File", 'does', 'not', 'exist'])
    if not ok:
        return False
    return output.strip() == 'File exists'


def sleep(sec: int, at_least: int = None):
    if not at_least:
        at_least = max(sec - 2 * sec // 3, 1)
    sec = random.randint(at_least, sec)
    time.sleep(sec)


class StoppableThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition.
    """

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def run_with_timeout(command, timeout, env=None) -> tuple[str, str, Error]:
    """

    :param command:
    :param timeout:
    :param env:
    :return:
    """

    def _run_command(cmd, e, q):
        result = subprocess.run(cmd, capture_output=True, env=e)
        q.put((result.stdout, result.stderr, result.returncode))

    if is_linux():
        pgid = os.getpid()
        os.setpgrp()

    output_q = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_run_command, args=(command, env, output_q))
    proc.start()
    proc.join(timeout)

    if proc.is_alive():
        if is_win():
            import psutil
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
        elif is_linux():
            import signal
            os.killpg(pgid, signal.SIGTERM)
        proc.join()
        err = TIMEOUT
        stdout = ""
        stderr = "超时"
    else:
        stdout, stderr, ret_code = output_q.get()
        err = OK if ret_code == 0 else INTERVAL_SERVER
    return stdout, stderr, err
