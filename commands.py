"""
Telegram command handlers for the server tools program.
"""

import os

def enable_ip_watcher(router, bot):
    router.config.config["ip_watcher_enabled"] = True
    router.config.save()
    router.start_ip_watcher()
    bot.send_message("Public IP watcher enabled. Monitoring for public IP changes every 5 minutes.")

def disable_ip_watcher(router, bot):
    router.config.config["ip_watcher_enabled"] = False
    router.config.save()
    router.stop_ip_watcher()
    bot.send_message("Public IP watcher disabled.")

def show_settings(router, bot):
    """Show all configuration settings from config files"""
    try:
        # Send a simple test message first
        print(f"DEBUG: show_settings called, router type: {type(router)}, config type: {type(router.config)}")
        bot.send_message("Settings command received!")
        
        # Then send the actual settings
        settings = ["🔧 Global Settings:"]
        
        if os.path.exists("configs/global.toml"):
            with open("configs/global.toml", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        settings.append(f"  {line}")
        
        settings.append("")
        settings.append("🌐 Router Settings:")
        if os.path.exists("configs/router.toml"):
            with open("configs/router.toml", "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "password" in line.lower():
                            key = line.split("=")[0].strip()
                            settings.append(f"  {key} = ***masked***")
                        else:
                            settings.append(f"  {line}")
        
        message = "\n".join(settings)
        bot.send_message(f"Current Settings:\n\n{message}")
        
    except Exception as e:
        bot.send_message(f"Error: {str(e)}")

# Command constants
CMD_ROUTER_IP = "/router_ip"
CMD_ROUTER_DEVICES = "/router_devices"
CMD_ROUTER_IP_WATCHER = "/router_ip_watcher"
CMD_PUBLIC_IP_WATCHER_ENABLE = "/public_ip_watcher_enable"
CMD_PUBLIC_IP_WATCHER_DISABLE = "/public_ip_watcher_disable"
CMD_SETTINGS = "/settings"

CMD_START = "/start"
CMD_HELP = "/help"

# Group router commands
ROUTER_COMMANDS = [
    CMD_ROUTER_IP,
    CMD_ROUTER_DEVICES,
    CMD_ROUTER_IP_WATCHER,
    CMD_PUBLIC_IP_WATCHER_ENABLE,
    CMD_PUBLIC_IP_WATCHER_DISABLE,
]

# Command handlers - functions that take (router, bot) and handle the command
COMMAND_HANDLERS = {
    CMD_ROUTER_IP: lambda router, bot: bot.send_message(f"Router IP Info:\n{router.get_ip_address()}"),
    CMD_ROUTER_DEVICES: lambda router, bot: bot.send_message(f"Connected Devices:\n{router.get_connected_devices()}"),
    #CMD_ROUTER_IP_WATCHER:,
    CMD_PUBLIC_IP_WATCHER_ENABLE: lambda router, bot: enable_ip_watcher(router, bot),
    CMD_PUBLIC_IP_WATCHER_DISABLE: lambda router, bot: disable_ip_watcher(router, bot),
    CMD_SETTINGS: lambda router, bot: show_settings(router, bot),
    CMD_HELP: lambda router, bot: bot.send_message("Available commands:\n" + "\n".join(sorted(COMMAND_HANDLERS.keys()))),
}

def handle_command(command, router, bot):
    """
    Handle a Telegram command.
    
    Args:
        command (str): The command received
        router: Router instance
        bot: TelegramBot instance
    
    Returns:
        bool: True if command was handled, False otherwise
    """
    if command in COMMAND_HANDLERS:
        try:
            COMMAND_HANDLERS[command](router, bot)
            return True
        except Exception as e:
            bot.send_message(f"Error executing {command}: {e}")
            return True
    return False