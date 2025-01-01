# app/telegram/telegram_client.py

import asyncio
import logging
from app.services.base_service import BaseService
from app.utils.config import Config

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logger = logging.getLogger(__name__)

class TelegramBotService(BaseService):
    def __init__(self, exchange_mediator, event_bus):
        self.application = Application.builder().token(
            Config.get_instance().get_config_value("telegram_bot").get("bot_token")
        ).build()
        self.event_bus = event_bus
        self.exchange_mediator = exchange_mediator
        self.bot_task = None  # Reference to the bot task

    async def start(self):
        logger.info("Starting Telegram Bot Service")

        # Add handlers
        self.application.add_handler(CommandHandler("start", TelegramBotService.command_start))
        self.application.add_handler(CommandHandler("help", TelegramBotService.command_help))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, TelegramBotService.echo)
        )

        # Initialize and start the application
        await self.application.initialize()
        await self.application.start()

        # Start polling in the background
        self.bot_task = asyncio.create_task(self.application.updater.start_polling())

        #self.application.start()

    async def stop(self):
        logger.info('Stopping Telegram bot service...')
        if self.bot_task:
            # Gracefully stop the bot
            await self.application.updater._stop_polling()
            await self.application.updater.stop()
            await self.application.updater.shutdown()
            await self.application.stop()
            await self.application.shutdown()
            # Cancel the bot task
            self.bot_task.cancel()
            try:
                await self.bot_task
            except asyncio.CancelledError:
                logger.info('telegram bot service cancelled')

    @staticmethod
    async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        await update.message.reply_html(
            rf"Hi {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )

    @staticmethod
    async def command_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""
        await update.message.reply_text("Help!")

    @staticmethod
    async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Echo the user message."""
        await update.message.reply_text(update.message.text)

        