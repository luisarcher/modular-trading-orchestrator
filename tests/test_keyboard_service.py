# tests/test_keyboard_service.py

import pytest
import asyncio
from app.events.event_bus import EventBus
from app.exchanges.mock_exchange_mediator import MockExchangeMediator
from app.message_handler import MessageHandler
from app.services.keyboard_service import KeyboardService
from app.exchanges.exchange_mediator import ExchangeMediator

@pytest.mark.asyncio
async def test_keyboard_buy_btc_command_history():
    # Initialize EventBus
    event_bus = EventBus()

    exchange_mediator = MockExchangeMediator()

    # Initialize and subscribe MessageHandler
    await MessageHandler.subscribe(event_bus, exchange_mediator)

    # Initialize KeyboardService
    keyboard_service = KeyboardService(event_bus)
    keyboard_task = asyncio.create_task(keyboard_service.start())

    # Allow some time for KeyboardService to publish the message
    await asyncio.sleep(0.5)

    # Stop KeyboardService
    await keyboard_service.stop()
    keyboard_task.cancel()
    try:
        await keyboard_task
    except asyncio.CancelledError:
        pass

    # Check command history
    assert len(MessageHandler.command_history) > 0
    last_command = MessageHandler.command_history[-1]
    assert last_command['action'] == 'buy'
    assert last_command['symbol'] == 'BTC'