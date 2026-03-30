# @Descr:工程目录锚点
import sys
from functools import lru_cache
from pathlib import Path
from typing import Optional


@lru_cache(maxsize=1)
def _path_anchor() -> Path:
    """
    获取工程目录锚点
    :return: 项目根目录的绝对路径
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parents[1]


def _get_storage_path(*subdirs: str) -> Path:
    """
    获取存储目录路径
    :param subdirs: 子目录路径
    :return: 完整路径
    """
    path = _path_anchor() / 'storage' 
    for subdir in subdirs:
        path = path / subdir
    path.mkdir(parents=True, exist_ok=True)
    return path


def path_config_folder() -> Path:
    """
    获取配置文件路径
    :return: 配置文件路径
    """
    return _get_storage_path('config')


def path_cache() -> Path:
    """
    获取缓存文件目录
    :return: 缓存文件目录
    """
    return _get_storage_path('temp', 'cache')


def path_log() -> Path:
    """
    获取日志文件目录
    :return: 日志文件目录
    """
    return _get_storage_path('log')


if __name__ == '__main__':
    print(_path_anchor())
    print(path_config_folder())
    print(path_cache())
    print(path_log())