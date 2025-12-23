import asyncio
import logging
import sys
import queue

import router_utils
import config
import telegram_bot
from config.logger import get_logger
from commands import handle_command

async def handle_commands_loop(command_queue, router, bot, logger):
    while True:
        try:
            # Non-blocking get with timeout
            while not command_queue.empty():
                command = command_queue.get_nowait()
                logger.info(f"Received message from Telegram: {command}")
                # Handle commands synchronously
                handle_command(command, router, bot)
            await asyncio.sleep(0.1)  # Small delay to prevent busy loop
        except Exception as e:
            logger.error(f"Error in command handling loop: {e}")
            await asyncio.sleep(1)

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
    
    log_level_str = global_config.get("log_level", "DEBUG")
    log_level = getattr(logging, log_level_str.upper(), logging.DEBUG)
    log_file = global_config.get("logging_file", "app.log")
    log_format = global_config.get("logging_format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logger = get_logger(log_file=log_file, level=log_level, log_format=log_format)
    logger.info("Logger initialized")
    
    try:
        telegram_config = config.Config("configs/telegram.toml", config_type=config.CONFIG_TELEGRAM, logger=logger)
        command_queue = queue.Queue()
        bot = telegram_bot.TelegramBot(telegram_config, logger=logger, command_queue=command_queue)
        bot.start()
        
    except Exception as e:
        logger.error(f"Error initializing Telegram bot: {e}")
        sys.exit(1)

    try:
        router_config = config.Config("configs/router.toml", config_type=config.CONFIG_ROUTER, logger=logger)
        router = router_utils.init_router_connection(router_config, logger=logger)
        router.set_message_callback(lambda msg: bot.send_message(msg))
        
    except Exception as e:
        logger.error(f"Error loading router configuration: {e}")
        sys.exit(1)


    # Main loop
    try:
        while True:
            try:
                command = command_queue.get(timeout=1) 
                print(f"Received message from Telegram: {command}")
                # Handle commands
                handle_command(command, router, bot)
            except queue.Empty:
                pass
    except KeyboardInterrupt:
        print("Shutting down...")
        disconnect_all(router, bot, logger)
    

if __name__ == "__main__":
    main()
    
# * TODO list
# TODO: add command for updating setting is different file
# TODO: use global ip not local for router watcher. ✅ DONE
# TODO: Better command for enabling and disabling watcher ip ✅ DONE
# TODO: When sending help command group the different commands to be abel to read it more easily.
# TODO: When sending router devices command format the output to a more readable state and check if it is posable to get device names as well as the mac and ip

