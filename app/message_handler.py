# app/message_handler.py

import logging


logger = logging.getLogger(__name__)

class MessageHandler:
    event_bus           = None
    exchange_mediator   = None
    command_history     = []

    @staticmethod
    def set_exchange_mediator(mediator):
        MessageHandler.exchange_mediator = mediator

    @staticmethod
    def set_event_bus(event_bus):
        MessageHandler.event_bus = event_bus

    @staticmethod
    async def handle_keyboard_message(msg):
        logger.info(f"Received keyboard message: {msg}")

        # command 'quit' to shutdown the app
        if 'quit' in msg.lower():
            await MessageHandler.event_bus.publish('shutdown', msg)

    @staticmethod
    async def handle_new_message(event):

        logger.info(f"Received new message: {event}")

        if MessageHandler.exchange_mediator is None:
            raise ValueError("Exchange Mediator is not set.")
        
        # Convert the event into a command
        command = MessageHandler.parse_event_to_command(event)
        
        # Keep command history
        MessageHandler.command_history.append(command)
        
        # Send the command to the Exchange Mediator
        await MessageHandler.exchange_mediator.execute_command(command)

    @staticmethod
    def parse_event_to_command(event):
        message_text = event.raw_text if hasattr(event, 'raw_text') else event
        if isinstance(message_text, str):
            parts = message_text.lower().split()
            if parts[0] == 'buy' and len(parts) > 1:
                return {'action': 'buy', 'symbol': parts[1].upper()}
            elif parts[0] == 'sell' and len(parts) > 1:
                return {'action': 'sell', 'symbol': parts[1].upper()}
        return {'action': 'unknown'}

    @staticmethod
    async def subscribe(event_bus, mediator):
        # Set the Exchange Mediator reference
        MessageHandler.set_exchange_mediator(mediator)
        MessageHandler.set_event_bus(event_bus)
        
        # Subscribe to relevant events
        event_bus.subscribe('telegram_new_message', MessageHandler.handle_new_message)
        event_bus.subscribe('keyboard_new_message', MessageHandler.handle_keyboard_message)