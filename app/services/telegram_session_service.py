# app/telegram/telegram_client.py

import logging
from telethon import TelegramClient, events
from app.services.base_service import BaseService
from app.utils.config import Config

logger = logging.getLogger(__name__)

class TelegramSessionService(BaseService):
    def __init__(self,event_bus):
        self.config = Config.get_instance()
        self.client = TelegramClient(
            'session_read', 
            self.config.get_config_value("telegram_api").get("api_id"), 
            self.config.get_config_value("telegram_api").get("api_hash")
        )
        self.event_bus = event_bus

        # Extract user IDs from YAML data
        self.user_ids    = self.config.get_config_value("telegram_api").get("user_ids")
        self.channel_ids = self.config.get_config_value("telegram_api").get("channel_ids")

    async def start(self):
        logger.info('Starting TelegramBotService...')
        await self.client.start(bot_token=self.bot_token)

        @self.client.on(events.NewMessage())
        async def handler(event):
            # Put the event in the message queue
            #with queue_lock:
                #message_queue.put(event)
            sender = await event.get_sender()
            #print(sender)
            #print(sender.username)

            #if (event.message.peer_id.user_id and event.message.peer_id.user_id in user_ids):

            logger.info('Received Telegram message:' + str(event.message.message[:10]) + "... from sender: " + str(sender))

            if (
                (hasattr(event.message.peer_id, 'user_id') and event.message.peer_id.user_id in self.user_ids)
                or (hasattr(event.message.peer_id, 'channel_id') and event.message.peer_id.channel_id in self.channel_ids)
            ):
                # use or for channels
                # or (event.message.peer_id.channel_id and event.message.peer_id.channel_id in channel_ids):
                logger.info('Handling message: ' + str(event.message.message[:10]))

            # Publish an event if needed
            await self.event_bus.publish('telegram_new_message', event)

        await self.client.start()
        await self.client.run_until_disconnected()

    async def stop(self):
        await self.client.disconnect()