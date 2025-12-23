import threading
import logging
import queue
import asyncio
import time
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
        self.running = False
        
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
        pass  # Removed, handled in handle_message
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = update.effective_chat.id
            text = update.message.text
            self.logger.info(f"Received message from chat {chat_id}: {text}")

            # Put all messages to queue for main loop to process
            self.command_queue.put(text)

            if text.startswith("/"):
                await update.message.reply_text(f"Command received: {text}")
            else:
                await update.message.reply_text("Message received but not a command.")
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            try:
                await update.message.reply_text("An error occurred while processing your message.")
            except Exception as reply_error:
                self.logger.error(f"Failed to send error reply: {reply_error}")
    
    def initialize(self):
        if self.token is None:
            raise ValueError("No bot token")
        try:
            self.app = ApplicationBuilder().token(self.token).build()
            self.logger.info("Telegram bot application built successfully")
        except Exception as e:
            self.logger.error(f"Failed to build Telegram bot application: {e}")
            raise
        
        # Add handlers
        self.app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message))
        self.app.add_handler(MessageHandler(filters.COMMAND, self.handle_message))
        self.logger.info("Telegram bot initialized with handlers")
    
    def run(self):
        self.running = True
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries and self.running:
            try:
                if self.app is None:
                    self.initialize()
                self.logger.info("Starting Telegram bot polling...")
                self.running = True
                # Note: Can't send startup message until user initiates conversation
                self.logger.info("Bot is ready to receive messages. Send /start or any message to test.")
                self.app.run_polling(stop_signals=None)
                # If run_polling() exits normally, break the loop
                break
            except Exception as e:
                retry_count += 1
                self.logger.error(f"Error running bot (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    self.logger.info("Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    self.logger.error("Max retries reached, stopping bot.")
                    self.running = False
                    self.disconnect()
                    raise ValueError(f"Failed to run bot after {max_retries} attempts: {e}")

    def start(self):
        try:
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            self.logger.info("Telegram bot started in a separate thread")
        except Exception as e:
            self.logger.error(f"Error starting bot thread: {e}")
            self.running = False
            self.disconnect()
            raise ValueError(f"Failed to start bot: {e}")

    def send_message(self, text):
        if self.app is None or not self.running:
            self.logger.warning("Bot not initialized or not running!")
            return
        try:
            bot: Bot = self.app.bot
            asyncio.run(bot.send_message(chat_id=self.chat_id, text=text))
            self.logger.info(f"Sent message: {text}")
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            # Optionally, disconnect on send error
            self.disconnect()

    def disconnect(self):
        self.running = False
        # Note: No need to explicitly stop the app since the thread is daemon and will die with the process
        # No need to join daemon threads


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