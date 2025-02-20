import os
import shutil
import zipfile

from common_tool.errno import Error, MISS_ZIP, BROKEN_ZIP, OK
from common_tool.log import logger

from ._path import get_file_path
from .filename import check_file_exist

_compress_suffix = {"gz", "tar", "zip", "rar", "tar.gz"}


def is_compress_file(filepath: str) -> bool:
    if "." not in filepath:
        return False
    suffix = filepath.split('.')[-1]
    return suffix in _compress_suffix


def check_zip_file(filepath: str) -> Error:
    """
    校验文件是否是完好的zip文件
    :param filepath:
    :return:
    """
    if not check_file_exist(filepath):
        return MISS_ZIP
    try:
        zip_f = zipfile.ZipFile(filepath)
    except Exception as e:
        logger.error(f"check_zip_file {filepath} get broken zip {e}")
        return BROKEN_ZIP
    else:
        if zip_f.testzip() is not None:
            logger.error(f"check_zip_file {filepath} get broken file")
            return BROKEN_ZIP
    return OK


def extract_compressed(path: str, target_path: str = None) -> Error:
    """
    解压压缩文件
    :param target_path:
    :param path:
    :return:
    """
    if not target_path:
        target_path = os.path.dirname(path)
    shutil.unpack_archive(path, target_path)
    return OK


def compress(path: str, target_path: str = None) -> tuple[str, Error]:
    path = get_file_path(path, "")
    if target_path is None:
        target_path = f"{path}"
    shutil.make_archive(target_path, "zip", path)
    return f"{target_path}.zip", OK
