"""
Telegram command handlers for the server tools program.
"""

# Command constants
CMD_ROUTER_IP = "/router_ip"
CMD_ROUTER_DEVICES = "/router_devices"
CMD_START = "/start"
CMD_HELP = "/help"

# Group router commands
ROUTER_COMMANDS = [
    CMD_ROUTER_IP,
    CMD_ROUTER_DEVICES,
]

# Command handlers - functions that take (router, bot) and handle the command
COMMAND_HANDLERS = {
    CMD_ROUTER_IP: lambda router, bot: bot.send_message(f"Router IP Info:\n{router.get_ip_address()}"),
    CMD_ROUTER_DEVICES: lambda router, bot: bot.send_message(f"Connected Devices:\n{router.get_connected_devices()}"),
    CMD_HELP: lambda router, bot: bot.send_message("Available commands:\n" + "\n".join(sorted(COMMAND_HANDLERS.keys()))),
    # Add more commands here easily
    # CMD_SOME_COMMAND: lambda router, bot: handle_some_command(router, bot),
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