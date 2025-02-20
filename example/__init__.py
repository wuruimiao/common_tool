from common_tool.server import init_base
from common_tool.data import format_file_name
from common_tool.server import MultiM

command = "example"

# init_base("config.yaml", log_f_prefix=f"{command}.{'.'.join([format_file_name(item) for item in argv])}")
init_base("config.yaml", log_f_prefix=f"{command}.{'.'.join([format_file_name(item) for item in argv[:1]])}")


def test():
    def do():
        from common_tool.log import logger
        logger.info("test")
    return do

MultiM.add_once_p("run_crawler_call", test)

MultiM.start()
