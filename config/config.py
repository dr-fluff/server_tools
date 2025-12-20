import tomllib
import tomli_w
import os
import logging

class Config:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self.config = {}
        
        self.load()
        self.validate()
    
    def load(self):
        if self.config_file_path is None:
            raise ValueError("Config file path cannot be None")
        
        if os.exists(self.config_file_path) is False:
            raise FileNotFoundError(f"Config file not found: {self.config_file_path}")
        
        try:
            with open(self.config_file_path, "rb") as f:
                self.config = tomllib.load(f)
        except Exception as e:
            logging.error(f"Failed to load config file: {e}")
            raise ValueError(f"Failed to load config file: {e}")
        
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

