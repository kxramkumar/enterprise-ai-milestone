import os
import yaml
from pathlib import Path
from typing import Dict, Type, Any


class SingletonMeta(type):
    _instances: Dict[Type[Any], Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Config(metaclass=SingletonMeta):
    __config = None

    def __init__(self, config: str):
        if self.__config is None:
            config_file = f"{config}"
            self.__config = Config.load(config_file)

    @staticmethod
    def config(config_file: str = "config.yml"):
        config = SingletonMeta._instances.get(Config)
        if config is None:
            config = Config(config=config_file)
        return config.__config

    @staticmethod
    def load(file_path):
        config_path = os.getenv("APP_CONFIG_PATH", file_path)
        config_path = Path(config_path).resolve()
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        dot_config = Config.flatten_dict(config)
        Config.override_with_env(dot_config)
        return dot_config

    @staticmethod
    def flatten_dict(data, parent_key="", delimiter="."):
        items = {}
        for key, value in data.items():
            new_key = f"{parent_key}{delimiter}{key}" if parent_key else key
            if isinstance(value, dict):
                items.update(Config.flatten_dict(value, new_key, delimiter=delimiter))
            else:
                items[new_key] = value
        return items

    @staticmethod
    def override_with_env(config_dict):
        for key in config_dict.keys():
            env_key = key.upper().replace(".", "_")
            if env_key in os.environ:
                try:
                    config_dict[key] = yaml.safe_load(os.environ[env_key])
                except yaml.YAMLError:
                    config_dict[key] = os.environ[env_key]

    @staticmethod
    def get(key: str):
        config = Config.config()
        if config is None:
            config = Config.config()

        if (config is not None) and (key in config):
            return config[key]
        return None

    @staticmethod
    def set(key: str, value: Any) -> Any:
        config = Config.config()

        if config is not None:
            config[key] = value
            return value
        return None
