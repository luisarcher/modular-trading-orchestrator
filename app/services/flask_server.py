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
        self.should_exit = asyncio.Event()
        self.server_task = None

        # Register before_serving and after_serving functions
        self.app.before_serving(self.before_serving)
        self.app.after_serving(self.after_serving)

    def setup_routes(self):
        @self.app.route('/')
        async def index():
            return 'Hello from Quart!'
        
        @self.app.route('/shutdown', methods=['GET'])
        async def shutdown():
            await self.event_bus.publish('shutdown', 'shutdown')
            return 'Shutting down...'

    async def before_serving(self):
        """Function to run before the server starts serving."""
        logger.info('Executing before serving tasks...')
        # Initialize resources or perform any setup here
        # Example: await self.event_bus.publish('server_starting', 'Quart server is starting')

    async def after_serving(self):
        """Function to run after the server stops serving."""
        logger.info('Executing after serving tasks...')
        # Clean up resources or perform any teardown here
        # Example: await self.event_bus.publish('server_stopped', 'Quart server has stopped')

    async def start(self):
        logger.info('Starting Flask (Quart) server...')

        # Define a shutdown_trigger function that waits until self.should_exit is set
        async def shutdown_trigger():
            await self.should_exit.wait()

        # Run the Quart app with the shutdown_trigger
        self.server_task = asyncio.create_task(
            self.app.run_task(
                host='0.0.0.0',
                port=5000,
                shutdown_trigger=shutdown_trigger
            )
        )

    async def stop(self):
        logger.info('Stopping Flask (Quart) server...')
        # Signal the shutdown_trigger to stop the server
        self.should_exit.set()
        # Wait for the server task to finish
        try:
            await self.server_task
        except asyncio.CancelledError:
            logger.info('Flask server task was cancelled.')
        except Exception as e:
            logger.error(f'An error occurred while stopping the Flask server: {e}')