import tomllib
import tomli_w
import os
import logging

from config import consts

class Config:
    def __init__(self, config_file_path: str, config_type: int = 0, logger: logging.Logger = None):
        self.config_file_path = config_file_path
        self.config = {}
        self.logger = logger
    
        try:
            self.load()
            self.validate()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error loading config: {e}")
            else:
                logging.error(f"Error loading config: {e}")
            self.init_default(config_type)
    
    def init_default(self, config_type: int):
        if config_type == consts.CONFIG_GLOBAL:
            self.create_default(consts.default_config_global)
        elif config_type == consts.CONFIG_TELEGRAM:
            self.create_default(consts.default_config_telegram)
        elif config_type == consts.CONFIG_ROUTER:
            self.create_default(consts.default_config_router)
        else:
            raise ValueError("Invalid config type")
    
    def load(self):
        if self.config_file_path is None:
            raise ValueError("Config file path cannot be None")
        
        if os.path.exists(self.config_file_path) is False:
            raise FileNotFoundError(f"Config file not found: {self.config_file_path}")
        
        try:
            with open(self.config_file_path, "rb") as f:
                self.config = tomllib.load(f)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to load config file: {e}")
            else:
                logging.error(f"Failed to load config file: {e}")
            raise ValueError(f"Failed to load config file: {e}")
        
        if not isinstance(self.config, dict):
            raise ValueError("Config file is not a valid TOML dictionary")
        
        if self.config is None:
            raise ValueError("Config file is empty or invalid")
        
        if self.config == {}:
            raise ValueError("Config file is empty")
    
    def create_default(self, default_config: dict):
        self.config = default_config
        self.save()
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)
    
    def print_config(self):
        for key, value in self.config.items():
            print(f"{key}: {value}")

    def save(self):
        tomli_w.dump(self.config, open(self.config_file_path, "wb"))
    
    def validate(self):
        pass
    
    def update(self, **kwargs):
        pass
    
    def reset_to_defaults(self):
        pass

