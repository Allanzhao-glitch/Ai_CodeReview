import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import time
from typing import Dict, Any, Optional

from tools import logger
from tools.tools_toml import TomlConfigManager


class ConfigManager:
    _instance: Optional['ConfigManager'] = None
    _config: Optional[Dict[str, Any]] = None
    _timestamp: float = 0

    CACHE_DURATION: float = 1.0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if ConfigManager._config is None:
            self._load()

    def _load(self, force: bool = False) -> Dict[str, Any]:
        current_time = time.time()
        
        if not force and ConfigManager._config is not None:
            if current_time - ConfigManager._timestamp <= ConfigManager.CACHE_DURATION:
                return ConfigManager._config

        try:
            config_manager = TomlConfigManager('config.toml')
            ConfigManager._config = config_manager.load_config()
            ConfigManager._timestamp = current_time
            self._log_reload(force)
            return ConfigManager._config

        except Exception as e:
            if ConfigManager._config is None:
                raise RuntimeError(f"配置加载失败: {e}") from e
            logger.warning(f"[CONFIG] 配置重载失败，使用旧配置: {e}")
            return ConfigManager._config

    def _log_reload(self, force: bool):
        config = ConfigManager._config
        ollama = config.get('OLLAMA', {})
        logger.debug(
            f"[CONFIG] 配置已{'强制重载' if force else '自动刷新'}: "
            f"RUNNING_MODE={ollama.get('RUNNING_MODE', 'N/A')}, "
            f"CURRENT_MODEL={ollama.get('CURRENT_MODEL', 'N/A')}, "
            f"DS={ollama.get('DS_MODEL', 'N/A')}, "
            f"QWEN={ollama.get('QWEN_MODEL', 'N/A')}"
        )

    def get(self) -> Dict[str, Any]:
        return self._load()

    def reload(self, force: bool = True) -> Dict[str, Any]:
        return self._load(force=force)


_config_manager = ConfigManager()


def get_config() -> Dict[str, Any]:
    return _config_manager.get()


def refresh_config(force: bool = True) -> Dict[str, Any]:
    return _config_manager.reload(force=force)


if __name__ == '__main__':
    print(get_config())
    print(refresh_config())