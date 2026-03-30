"""
@Explain   :日志相关
"""
import sys
from pathlib import Path
import logging
import os
from datetime import datetime
from typing import Optional, List
from basics.basics_path import path_log


DEFAULT_FORMAT = '[%(asctime)s.%(msecs)03d] -[%(levelname)s] -[%(module)s->%(funcName)s->line:%(lineno)d] : %(message)s'
DEFAULT_DATEFMT = '%Y-%m-%d  %H:%M:%S'


class LogConfig:
    log_path: Path = path_log()
    log_name_base: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_name: str = f'Program_{log_name_base}.log'
    log_file_path: Path = log_path / log_name


class CToolsLog:
    _instances: dict = {}

    def __new__(cls, name: Optional[str] = None, console_out: bool = True, file_out: bool = False):
        key = name or 'default'
        if key not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[key] = instance
        return cls._instances[key]

    def __init__(self, name: Optional[str] = None, console_out: bool = True, file_out: bool = False):
        if self._initialized:
            return
        self._initialized = True
        
        self.logger = logging.getLogger(name or __name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()

        formatter = logging.Formatter(fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATEFMT)

        if console_out:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
        
        if file_out:
            file_handler = logging.FileHandler(LogConfig.log_file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    @property
    def handlers(self) -> List[logging.Handler]:
        return self.logger.handlers[:]
    
    def close_handlers(self):
        for handler in self.logger.handlers[:]:
            handler.flush()
            handler.close()
        self.logger.handlers.clear()


if __name__ == "__main__":
    logger = CToolsLog(name='root_logger', file_out=True).logger
    logger.debug("debug message")
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")