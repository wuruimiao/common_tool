import json

import aiohttp

from .header import AntiHeader


async def async_get(url: str, params: dict, timeout: int = 100) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=timeout, hearders=AntiHeader) as resp:
            result = await resp.text()
            return json.loads(result)
