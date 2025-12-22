default_global_config_path = "configs/global.toml"
default_telegram_config_path = "configs/telegram.toml"
default_router_config_path = "configs/router.toml"

default_config_global = {
    "log_level": "INFO",
    "logging_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "logging_file": "app.log",
}

default_config_telegram = {
    "bot_name": "",
    "bot_username": "",
    "token": "",
    "chat_id": ""
}

default_config_router = {
    "ssh_hostname": "192.168.1.1",
    "ssh_key_path": "",
    "username": "",
    "password": "",
    "ssh_port": 22,
}

CONFIG_GLOBAL = 0
CONFIG_TELEGRAM = 1
CONFIG_ROUTER = 2