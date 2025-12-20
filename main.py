from rich import print
from config.config import Config
import logging
import sys

def main() -> None:
    try:
        global_config = Config("configs/global.toml")
    except Exception as e:
        print(f"[red]Error loading global configuration: {e}[/red]")
        sys.exit(1)
    
    logger = logging.getLogger(__name__)
    logger.setLevel(global_config.get("log_level", "INFO"))
    logger.info("Logger initialized")
    
    telegram_config = Config("configs/telegram.toml")
    telegram_config.print_config()

if __name__ == "__main__":
    main()