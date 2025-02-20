import platform


def is_win() -> bool:
    """
    是否运行在windows下
    :return:
    """
    return platform.system().lower() == 'windows'


def is_linux() -> bool:
    """
    是否运行在linux下
    :return:
    """
    return platform.system().lower() == 'linux'


def fix_win_focus():
    """
    防止鼠标误触导致阻塞，但也会导致不响应ctrl+c
    :return:
    """
    print(f"patch windows console")
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)
