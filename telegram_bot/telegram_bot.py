import threading
import logging
import queue
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


class TelegramBot:
    def __init__(self, telegram_config, logger=None, command_queue=None):
        self.telegram_config = telegram_config
        self.token = telegram_config.get("token")
        self.chat_id = telegram_config.get("chat_id")
        self.logger = logger or logging.getLogger(__name__)
        self.thread = None
        self.app = None
        self.command_queue = command_queue or queue.Queue()
        
        if self.token is None or self.chat_id is None:
            raise ValueError("No token or chat id")
    
    def print_config(self):
        print("Telegram Bot Config:")
        for key, value in self.telegram_config.config.items():
            if key in ["token", "bot_token"]:
                print(f"{key}: {'*' * len(str(value)) if value else None}")
            else:
                print(f"{key}: {value}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Bot is running!")
        
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text
        self.logger.info(f"Received message: {text}")

        if text.startswith("/"):
            self.command_queue.put(text)  # Send command to main thread
            await update.message.reply_text(f"Command received: {text}")
        else:
            await update.message.reply_text("Message received but not a command.")
    
    def initialize(self):
        if self.token is None:
            raise ValueError("No bot token")
        self.app = ApplicationBuilder().token(self.token).build()
        
        # Add handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        self.app.add_handler(MessageHandler(filters.COMMAND, self.handle_message))
    
    def run(self):
        try:
            if self.app is None:
                self.initialize()
            self.logger.info("Starting Telegram bot polling...")
            self.app.run_polling()
        except Exception as e:
            self.logger.error("Error running bot")

    def start(self):
        try:
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.logger.info("Telegram bot started in a separate thread")
        except Exception as e:
            self.logger.error("Error starting bot")

    def send_message(self, text):
        """Send a message to the configured chat."""
        if self.app is None:
            self.logger.warning("Bot not initialized!")
            return
        bot: Bot = self.app.bot
        bot.send_message(chat_id=self.chat_id, text=text)

    def disconnect(self):
        """Stop the bot gracefully."""
        if self.app:
            self.logger.info("Stopping Telegram bot...")
            self.app.stop()
        if self.thread:
            self.thread.join()


def init_telegram_bot(telegram_config, logger) -> TelegramBot:
    try:
        bot = TelegramBot(telegram_config, logger)
    except Exception as e:
        logger.error(f"Error initializing Telegram bot: {e}")
        raise e
    return bot

def init_bot_threaded(bot: TelegramBot, logger) -> TelegramBot:
    logger.info("Telegram bot started in a separate thread")
    bot.start()
    return bot