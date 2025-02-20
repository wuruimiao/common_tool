from common_tool.errno import Error, OK


def init_base(conf_path: str = None, log=None, qs=None, global_conf=None, log_f_prefix: str = "") -> Error:
    init_log(conf_path, global_conf, log, log_f_prefix)
    init_sync(qs)
    return OK


def init_log(conf_path: str = None, global_conf=None, log_q=None, log_f_prefix: str = ""):
    from common_tool.log import logger
    if global_conf:
        from common_tool.config import init_global_conf
        init_global_conf(global_conf)
    elif conf_path:
        from common_tool.config import init_conf
        err = init_conf(conf_path, log_f_prefix)
        if not err.ok:
            logger.error(f"{conf_path} init {err}")
            return err

    from common_tool.log.q import QLogM
    if log_q:
        QLogM.init_q(log_q)
    from common_tool.log.log import init
    from common_tool.config import log_conf
    init(log_conf())


def init_sync(qs=None, sems=None, locks=None, rlocks=None, counters=None):
    from .sync import QM, SemM, LockM, RLockM, CounterM
    if qs:
        QM.init_by_list(qs)

    if sems:
        SemM.init_by_list(sems)

    if locks:
        LockM.init_by_list(locks)

    if rlocks:
        RLockM.init_by_list(rlocks)

    if counters:
        CounterM.init_by_list(counters)
