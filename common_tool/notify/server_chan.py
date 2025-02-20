import urllib.parse
import urllib.request

from common_tool.log import logger


class ServerChan:
    def _config(self):
        from common_tool.config import get_global_config
        return get_global_config().get("server_chan", {})

    def deployed(self):
        return not not self._config()

    def _send_key(self):
        key = self._config().get("send_key", "")
        if not key:
            logger.error(f"server chan need config send_key")
        return key

    def send(self, text, des="", key=""):
        if not key:
            key = self._send_key()
        content = urllib.parse.urlencode({"text": text, "desp": des}).encode("utf-8")
        url = f"https://sctapi.ftqq.com/{key}.send"
        req = urllib.request.Request(url, data=content, method="POST")
        with urllib.request.urlopen(req) as response:
            result = response.read().decode("utf-8")
        return result
