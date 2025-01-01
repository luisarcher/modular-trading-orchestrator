# app.py

import asyncio
import logging
import sys
from app.events.event_bus import EventBus
from app.exchanges.binance_exchange import BinanceExchange
from app.exchanges.exchange_mediator import ExchangeMediator
from app.exchanges.mock_exchange_mediator import MockExchangeMediator
from app.message_handler import MessageHandler
from app.services.flask_server import FlaskService
from app.services.keyboard_service import KeyboardService
from app.services.telegram_bot_service import TelegramBotService
#from app.discord.discord_client import DiscordService
from app.utils.config import Config

logger = logging.getLogger(__name__)

async def main():
    # Load configuration
    config = Config()

    # Initialize EventBus
    event_bus = EventBus()

    # Initialize Exchange Mediator
    # exchange_mediator = ExchangeMediator(BinanceExchange())
    # exchange_mediator.start()  # Assuming there's an async initialization

    exchange_mediator = MockExchangeMediator(None)
    await exchange_mediator.start()

    # Initialize and subscribe MessageHandler
    await MessageHandler.subscribe(event_bus, exchange_mediator)

    # Initialize Services
    # flask_service = FlaskService(event_bus)

    telegram_bot_service = TelegramBotService(event_bus, exchange_mediator)

    # telegram_session_service = TelegramSessionService(
    #    config.get_config_value("telegram_api").get("api_id"), 
    #    config.get_config_value("telegram_api").get("api_hash")
    #     event_bus=event_bus
    # )
    # discord_service = DiscordService(
    #     token=config.DISCORD_TOKEN,
    #     event_bus=event_bus
    # )
    keyboard_service = KeyboardService(event_bus)

    # Define Shutdown Handler
    async def shutdown_handler(_):
        #await flask_service.stop()
        await telegram_bot_service.stop()
        # await discord_service.stop()
        await keyboard_service.stop()
        exchange_mediator.stop()
        event_bus_task.cancel()

    # Subscribe Shutdown Handler
    event_bus.subscribe('shutdown', shutdown_handler)

    # Start EventBus
    event_bus_task = asyncio.create_task(event_bus.start())

    # Start Services
    services = [
        # asyncio.create_task(flask_service.start()),
        asyncio.create_task(telegram_bot_service.start()),
        # asyncio.create_task(discord_service.start()),
        asyncio.create_task(keyboard_service.start())
    ]

    try:
        await asyncio.gather(*services)
    except asyncio.exceptions.CancelledError:
        try:
            tasks = asyncio.all_tasks()
            for task in tasks:
                task.cancel()
        except Exception as e:
            logger.error(f"Forcing program termination...")
            sys.exit(1)
    finally:
        for service in services:
            service.cancel()
        await event_bus_task

if __name__ == '__main__':
    asyncio.run(main())