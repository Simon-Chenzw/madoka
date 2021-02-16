import importlib
import json
import logging
import os
import pkgutil
from types import ModuleType
from typing import Any, Dict, Iterable, List, Optional


class EnvJson:
    """
    json file should be `Dict[str,Any]` \n
    Every data request will read and parse the json file,
    please do not store large amounts of data
    """
    def __init__(self, path: str) -> None:
        self.path = path
        if not os.path.isfile(self.path):
            raise FileNotFoundError(f"{os.path.abspath(self.path)} not found")

    def __getitem__(self, key: str) -> Any:
        with open(self.path, 'r', encoding='utf-8') as fp:
            data: Dict[str, Any] = json.load(fp)
        return data[key]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        with open(self.path, 'r', encoding='utf-8') as fp:
            data: Dict[str, Any] = json.load(fp)
        return data.get(key, default)

    def save(self, key: str, value: Any) -> None:
        with open(self.path, 'w+', encoding='utf-8') as fp:
            data: Dict[str, Any] = json.load(fp)
            data[key] = value
            json.dump(data, fp, indent=4, ensure_ascii=False, sort_keys=True)


def loadAll(
    path: Iterable[str],
    prefix: str,
    ignore: List[str] = [],
) -> Dict[str, ModuleType]:
    """
    call it at plugin/__init__.py
    :path: `__path__`
    :prefix: `__name__`
    """
    logger = logging.getLogger('madoka')
    plugin: Dict[str, ModuleType] = {}
    if prefix[-1] != '.':
        prefix += '.'
    for moduleInfo in pkgutil.iter_modules(path, prefix):
        name = moduleInfo.name
        if name.split('.')[-1] not in ignore:
            plugin[name] = importlib.import_module(name)
        else:
            logger.debug(f"ignore module: {name}")
    name_list = [f"'{name.split('.')[-1]}'" for name in plugin]
    logger.info(f"load: {' '.join(name_list)}")
    return plugin


def setLogging(
    level: int = logging.INFO,
    activeFile: bool = False,
    dir='log',
    name='madoka.log',
):
    logger = logging.getLogger()
    logger.setLevel(level)

    try:
        from rich.logging import RichHandler
    except:
        pass
    else:
        console_handler = RichHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter("[%(name)s] %(message)s"))
        logger.addHandler(console_handler)

    if activeFile:
        from logging.handlers import TimedRotatingFileHandler

        if not os.path.isdir(dir):
            os.makedirs(dir)
        fname = os.path.join(dir, name)

        file_handler = TimedRotatingFileHandler(fname, when="midnight")
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s"))
        logger.addHandler(file_handler)
