from rich import print
import logging
import sys
import queue

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
    
    try:
        telegram_config = config.Config("configs/telegram.toml", config_type=config.CONFIG_TELEGRAM, logger=logger)
        command_queue = queue.Queue()
        bot = telegram_bot.TelegramBot(telegram_config, command_queue=command_queue)
        bot.print_config()
        bot.start()
        
    except Exception as e:
        logger.error(f"Error initializing Telegram bot: {e}")
        sys.exit(1)

    try:
        router_config = config.Config("configs/router.toml", config_type=config.CONFIG_ROUTER, logger=logger)
        router = router_utils.init_router_connection(router_config, logger=logger)
        
    except Exception as e:
        logger.error(f"Error loading router configuration: {e}")
        sys.exit(1)


    # Main loop
    while True:
        try:
            command = command_queue.get(timeout=1)  # Wait for commands from bot
            print(f"Processing command from Telegram: {command}")
            # Here you can handle the command in your main program
        except queue.Empty:
            pass
    
        if KeyboardInterrupt:
            print("Shutting down...")
            disconnect_all(router, bot, logger)
            break
    

if __name__ == "__main__":
    main()