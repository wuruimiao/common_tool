import traceback
import urllib.request
from urllib.error import HTTPError
from urllib.parse import urljoin

from m3u8.httpclient import HTTPSHandler
from .header import AntiHeader
from utils.log import logger


class DefaultHTTPClient:
    def __init__(self, http_proxy=None):
        self.proxies = {"http": http_proxy, "https": http_proxy} if http_proxy else None

    def download(self, uri, timeout=5, headers=None, verify_ssl=True):
        if not headers:
            headers = AntiHeader
        proxy_handler = urllib.request.ProxyHandler(self.proxies)
        https_handler = HTTPSHandler(verify_ssl=verify_ssl)
        opener = urllib.request.build_opener(proxy_handler, https_handler)
        opener.addheaders = headers.items()

        i = 0
        while True:
            try:
                resource = opener.open(uri, timeout=timeout)
                break
            except HTTPError as e:
                logger.error(f"DefaultHTTPClient download {uri} {traceback.format_exc()}")
                i += 1
                if i >= 10:
                    raise e
                logger.error(f"DefaultHTTPClient download retry {uri} {i}")
        base_uri = urljoin(resource.geturl(), ".")
        data = resource.read()
        try:
            content = data.decode(
                resource.headers.get_content_charset(failobj="utf-8")
            )
        except UnicodeDecodeError as e:
            logger.error(f"DefaultHTTPClient download {uri}")
            raise e
        return content, base_uri
