import json
import os

import yaml

from utils.errno import Error, MISS_JSON, OK, BROKEN_JSON
from utils.log import logger

from ._path import norm_path
from .filename import check_file_exist


def load_json_f(filename: str) -> tuple[dict, Error]:
    """
    加载json文件
    :param filename:
    :return:
    """
    res = {}
    if not check_file_exist(filename):
        return res, MISS_JSON
    with open(filename, "r", encoding="utf-8") as f:
        err = OK
        try:
            res = json.load(f)
        except ValueError:
            err = BROKEN_JSON
            logger.error(f"load_json_f {filename} broken json")
    return res, err


def dump_json_f(filename: str, _dict: dict) -> Error:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(_dict, f, ensure_ascii=False)
    return OK


def compare_json_f(path1: str, path2: str, exclude_field: set = None) -> bool:
    if not exclude_field:
        exclude_field = {}
    json1, err = load_json_f(path1)
    if not err.ok:
        logger.error(f"!!!!!!!!!no {path1}")
        return False
    json2, err = load_json_f(path2)
    if not err.ok:
        logger.error(f"!!!!!!!!!no {path2}")
        return False
    for k, v in json1.items():
        if k in exclude_field:
            continue
        if v != json2.get(k):
            return False
    return True


def tran_json_to_yml_f(json_path: str, yml_path: str):
    """
    json文件转换为yaml文件
    :param json_path:
    :param yml_path:
    :return:
    """
    yml_path = norm_path(yml_path)
    logger.info(f"tran_json_to_yml_f {json_path} to {yml_path}")
    if not check_file_exist(json_path):
        logger.error(f"trans_json_to_yml_f no {json_path}, do nothing")
        return
    if os.path.exists(yml_path):
        logger.error(f"trans_json_to_yml_f {yml_path} exist, do nothing")
        return

    with open(json_path, encoding="utf-8") as f:
        conf = json.load(f)

    with open(yml_path, 'w', encoding="utf-8") as f:
        yaml.dump(conf, f, allow_unicode=True, default_flow_style=False)
