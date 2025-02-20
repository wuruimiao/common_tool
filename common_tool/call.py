import asyncio
from common_tool.errno import OK, TIMEOUT
from common_tool.log import logger


async def con_async(tasks, con_num=3):
    """
    tasks传None，默认返回OK
    """
    result = [OK] * len(tasks)  # Initialize the result list with None
    index_map = {}  # Map task index to its position in the result list
    non_none_tasks_indices = []  # Keep track of indices for non-None tasks

    for i, task in enumerate(tasks):
        if task is not None:
            index_map[i] = len(non_none_tasks_indices)
            non_none_tasks_indices.append(i)

    for i in range(0, len(non_none_tasks_indices), con_num):
        batch_indices = non_none_tasks_indices[i:i + con_num]
        batch_tasks = [tasks[index] for index in batch_indices]
        res = await asyncio.gather(*batch_tasks, return_exceptions=True)

        for j, task_result in enumerate(res):
            result[batch_indices[j]] = task_result

    return result


def call_async(func, *ret):
    try:
        return asyncio.get_event_loop().run_until_complete(func)
    except asyncio.CancelledError:
        logger.error(f"{func.__name__} canceled")
        if ret:
            return *ret, TIMEOUT
        return TIMEOUT
