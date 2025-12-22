from rich import print
import logging
import sys

import router_utils
import config
import telegram_bot

def disconnect_all(router: router_utils.Router, telegram_bot: telegram_bot.TelegramBot, logger: logging.Logger) -> None:
    try:
        router.disconnect()
        logger.info("Router disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting router: {e}")
    
    try:
        telegram_bot.disconnect()
        logger.info("Telegram bot disconnected successfully")
    except Exception as e:
        logger.error(f"Error disconnecting Telegram bot: {e}")

def main() -> None:
    try:
        global_config = config.Config("configs/global.toml", config_type=config.CONFIG_GLOBAL)
    except Exception as e:
        print(f"[red]Error loading global configuration: {e}[/red]")
        sys.exit(1)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(global_config.get("log_level", "INFO"))
    logger.info("Logger initialized")

    # telegram_config = config.Config("configs/telegram.toml", config_type=config.CONFIG_TELEGRAM, logger=logger)
    # telegram_bot.init(telegram_config, logger=logger)

    try:
        router_config = config.Config("configs/router.toml", config_type=config.CONFIG_ROUTER, logger=logger)
    except Exception as e:
        logger.error(f"Error loading router configuration: {e}")
        sys.exit(1)

    router = router_utils.init_router_connection(router_config, logger=logger)
    
    disconnect_all(router, None, logger)

if __name__ == "__main__":
    main()