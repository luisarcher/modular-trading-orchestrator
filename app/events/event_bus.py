# app/events/event_bus.py

import asyncio
import logging
from typing import Callable, Dict, List, Any

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, event_type: str, data: Any):
        await self._queue.put((event_type, data))

    async def start(self):
        while True:
            try:
                event_type, data = await self._queue.get()
                handlers = self._subscribers.get(event_type, [])
                for handler in handlers:
                    # Schedule handler coroutines
                    asyncio.create_task(handler(data))
                self._queue.task_done()
            except asyncio.exceptions.CancelledError:
                logger.error("EventBus cancelled")
                break
            
