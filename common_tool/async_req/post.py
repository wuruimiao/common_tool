import json

import aiohttp

from .header import AntiHeader


async def async_post(url: str, data=None, headers: dict = None, timeout: int = 100) -> dict:
    if not headers:
        headers = {}
        async with aiohttp.ClientSession() as session:
            headers.update(AntiHeader)
            async with session.post(url, data=data, headers=headers, timeout=timeout) as resp:
                result = await resp.text()
                return json.loads(result)
