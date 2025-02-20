import asyncio
from typing import Union
from io import BytesIO
import aiofiles
import aiohttp

from common_tool.errno import Error, OK, ASYNC_DOWNLOAD, TIMEOUT
from common_tool.log import logger
from common_tool.system import DEFAULT_TIMEOUT

from .header import AntiHeader


async def _read_res(res):
    while True:
        err = OK
        chunk = None
        try:
            chunk = await res.content.read(1024)
        except aiohttp.ClientPayloadError:
            err = ASYNC_DOWNLOAD
        except asyncio.TimeoutError:
            err = TIMEOUT
        yield chunk, err
        if not err.ok or not chunk:
            break


# TODO：add url check
async def async_download(url: str, target: Union[str, BytesIO], params: dict = None, headers: dict = None,
                         timeout: int = DEFAULT_TIMEOUT, proxy: str = None) -> Error:
    if not headers:
        headers = {}

    session_timeout = aiohttp.ClientTimeout(
        total=None, sock_connect=timeout, sock_read=timeout)
    async with aiohttp.ClientSession(
            timeout=session_timeout,
            connector=aiohttp.TCPConnector(verify_ssl=False),
    ) as session:
        headers.update(AntiHeader)
        try:
            async with session.get(url, params=params, timeout=timeout, headers=headers, proxy=proxy) as res:
                logger.debug(f"async_download {url} to {target}")
                if isinstance(target, str):
                    # 文件
                    async with aiofiles.open(target, 'wb') as f:
                        async for chunk, err in _read_res(res):
                            if not err.ok:
                                return err
                            await f.write(chunk)
                else:
                    # 内存
                    async for chunk, err in _read_res(res):
                        if not err.ok:
                            return err
                        target.write(chunk)
                    target.seek(0)
        except (aiohttp.ClientConnectorError, aiohttp.ClientConnectorSSLError) as e:
            logger.error(f"async_download aio connect err={e}")
            return ASYNC_DOWNLOAD

    return OK


async def async_download_binary(url: str, params: dict = None, headers: dict = None,
                                timeout: int = 100) -> bytes:
    if not headers:
        headers = {}

    async with aiohttp.ClientSession() as session:
        headers.update(AntiHeader)
        async with session.get(url, params=params, timeout=timeout, headers=headers) as resp:
            data = []
            while True:
                chunk = await resp.content.read(1024)
                if not chunk:
                    break
                data.append(chunk)
            return b"".join(data)
