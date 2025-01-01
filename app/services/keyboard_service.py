# app/services/keyboard_service.py

import logging
import sys

import aioconsole
from app.services.base_service import BaseService
import asyncio

logger = logging.getLogger(__name__)

class KeyboardService(BaseService):
    def __init__(self, event_bus):
        super().__init__()
        self.event_bus = event_bus
        self._running = False
        self.listen_task = None  # Keep a reference to the task

    async def start(self):
        self._running = True
        logger.info('Starting KeyboardService...')
        self.listen_task = asyncio.create_task(self.listen_keyboard())

    async def listen_keyboard(self):
        while self._running:
            message = await self.get_keyboard_input()
            await self.event_bus.publish('keyboard_new_message', message)

    async def get_keyboard_input(self, test=False, test_command=None):
        if test:
            return test_command
        return await aioconsole.ainput()

    # async def get_keyboard_input(self, test=False, test_command=None):
    #     if test:
    #         return test_command
    #     loop = asyncio.get_event_loop()
    #     return await loop.run_in_executor(None, input)

    async def stop(self):
        logger.info('Stopping Keyboard service...')
        self._running = False
        if self.listen_task:
            self.listen_task.cancel()  # Cancel the task
            try:
                await self.listen_task  # Wait for the task to finish
            except asyncio.CancelledError:
                pass