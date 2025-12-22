import os
import threading
import logging

class TelegramBot:
    def __init__(self, telegram_config):
        self.token = ""
        self.chat_id = ""

    def send_message(self, chat_id, text):
        # Logic to send a message via Telegram API
        pass

    def receive_updates(self):
        # Logic to receive updates from Telegram API
        pass
    
    def run(self):
        print("Starting Telegram bot...")
        self.updater.start_polling()
        self.updater.idle()
    
    
def init_bot_and_run(bot_config) -> TelegramBot:
    bot = TelegramBot(bot_config)
    bot_thread = threading.Thread(target=bot.run)
    bot_thread.daemon = True
    bot_thread.start()
    return bot
