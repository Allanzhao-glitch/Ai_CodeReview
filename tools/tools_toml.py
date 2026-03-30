# import sys
from pathlib import Path
# sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import toml
from basics.basics_path import path_config_folder
from typing import Dict, Any, Optional
class TomlConfigManager:
    """
    TOML配置类
    """
    def __init__(self, config_path :Optional[str] = None):
        '''
        初始化TOML配置类
        :param config_path: 配置文件路径
        '''
        if config_path:
            self.config_path = path_config_folder() / config_path
        else:
            self.config_path = path_config_folder() / 'test.toml'
    
    def load_config(self,config_path :Optional[str] = None) -> Dict[str,Any]:
        '''
        加载TOML配置
        :param config_path: 配置文件路径
        :return: 配置字典
        '''
        path = self._get_path(config_path)
        try:
            with open(path,'r',encoding='utf-8') as f:
                config = toml.load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f'配置文件 {path} 不存在')
        except Exception as e:
            raise Exception(f'加载配置文件 {path} 失败: {e}')
        
    def save_config(self,config :Dict[str,Any],config_path :Optional[str] = None) -> bool:
        '''
        保存TOML配置
        :param config: 配置字典
        :param config_path: 配置文件路径
        :return: 保存成功返回True，否则返回False
        '''
        path = self._get_path(config_path)
        try:
            with open(path,'w',encoding='utf-8') as f:
                toml.dump(config,f)
            return True
        except Exception as e:
            raise Exception(f'保存配置文件 {path} 失败: {e}')

    def _get_path(self,config_path :Optional[str] = None) -> Path:
        '''
        获取配置文件路径
        :param config_path: 配置文件路径
        :return: 配置文件路径
        '''
        if config_path:
            return path_config_folder() / config_path
        return self.config_path

    def copy_config(self,config_path :Optional[str] = None) -> bool:
        '''
        复制配置文件
        :param config_path: 配置文件路径
        :return: 复制成功返回True，否则返回False
        '''
        try:
            config = self.load_config(config_path)
            return self.save_config(config,config_path)
        except Exception as e:
            print(f"复制配置文件时出错: {e}")
            return False
        
    def get_config_value(self, key_path: str, config_data: Optional[Dict[str, Any]] = None) -> Any:
        '''
        获取配置值
        :param key_path: 配置键路径，例如 "database.host"
        :param config_data: 配置字典
        :return: 配置值
        '''
        if config_data is None:
            config_data = self.load_config()
        keys = key_path.split('.')
        value = config_data
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            raise KeyError(f"配置键未找到: {key_path}")
        
    def set_config_value(self, key_path: str, value: Any, config_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        '''
        设置配置值
        :param key_path: 配置键路径，例如 "database.host"
        :param value: 配置值
        :param config_data: 配置字典
        :return: 配置字典
        '''
        if config_data is None:
            config_data = self.load_config()
        keys = key_path.split('.')
        config = config_data

        for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
        config[keys[-1]] = value 
        return config_data
    

def load_toml_config(config_path :Optional[str] = None) -> Dict[str,Any]:
    '''
    加载TOML配置
    :param config_path: 配置文件路径
    :return: 配置字典
    '''
    manager = TomlConfigManager()
    return manager.load_config()


def save_toml_config(config :Dict[str,Any],config_path :Optional[str] = None) -> bool:
    '''
    保存TOML配置
    :param config: 配置字典
    :param config_path: 配置文件路径
    :return: 保存成功返回True，否则返回False
    '''
    manager = TomlConfigManager()
    return manager.save_config(config,config_path)




if __name__ == "__main__":
    # 使用类的方式
    config_manager = TomlConfigManager('config.toml')

    # 加载配置
    data = config_manager.load_config()

    # 保存配置到另一个文件
    #config_manager.save_config(data, 'config1.toml')

    print(data)