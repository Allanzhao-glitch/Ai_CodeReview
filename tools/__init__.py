from tools.tools_loger import CToolsLog
from tools.tools_toml import TomlConfigManager

logger = CToolsLog(name='root_logger', file_out=True).logger

config = TomlConfigManager('config.toml').load_config()

__all__ = [
    "logger",
    "config"
]
