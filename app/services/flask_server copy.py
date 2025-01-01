# app/web/flask_server.py (Using Quart for Async)

import logging
from quart import Quart
from app.services.base_service import BaseService
import asyncio

logger = logging.getLogger(__name__)

class FlaskService(BaseService):
    def __init__(self, event_bus):
        self.app = Quart(__name__)
        self.event_bus = event_bus
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        async def index():
            return 'Hello from Quart!'
        
        @self.app.route('/shutdown', methods=['GET'])
        async def shutdown():
            await self.event_bus.publish('shutdown', 'shutdown')
            return 'Shutting down...'
        
    async def start(self):
        logger.info('Starting Flask server...')
        self.server = asyncio.create_task(self.app.run_task(host='0.0.0.0', port=5000))

    async def stop(self):
        logger.info('Stopping Flask server...')
        await self.app.shutdown()
        self.server.cancel()
        await asyncio.sleep(0)  # Allow cancellation
