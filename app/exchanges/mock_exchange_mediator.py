
# get logger
import logging
import threading
import time

logger = logging.getLogger(__name__)


class MockExchangeMediator:

    def __init__(self, exchange):
        self.__exchange = exchange
        self.is_running = False

    async def start(self):
        if not self.is_running:
            self.is_running = True
            logger.info('[Mock exchange] Starting MockExchangeMediator...')
            threading.Thread(target=self.__query_positions).start()

    def stop(self):
        self.is_running = False

    def execute_command(self, command):
        logger.info(f'[Mock exchange] Executing command: {command}')

    def __query_positions(self):
        while self.is_running:
            logger.info(f'[Mock exchange] Positions: Simulating exchange.get_current_positions()')
            time.sleep(8)

    