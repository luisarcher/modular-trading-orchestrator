import logging
from binance.client import Client
from dateutil import parser
from datetime import timedelta

from app.utils.config import Config

logger=logging.getLogger(__name__)


class BinanceExchange:

    def __init__(self) -> None:
        
        config = Config()

        self.collateral = config.get_config_value("binance_api").get("collateral")
        self.client = Client(
            config.get_config_value("binance_api").get("api_key"), 
            config.get_config_value("binance_api").get("api_secret")
        )
        self.exchange_info = self.client.futures_exchange_info()
        #self.sync_time_with_binance()
        self.account_info = self.client.futures_account()

    def sync_time_with_binance(self) -> None:
        server_time = self.client.get_server_time()['serverTime']
        system_time = parser.parse(self.client.get_system_status()['serverTime'])
        time_diff = system_time - timedelta(milliseconds=server_time)

        self.client.timestamp_offset = time_diff.total_seconds() * 1000

    def get_wallet_balance(self) -> float:
        #print(self.account_info)

        for asset in self.account_info['assets']:
            if asset['asset'] == self.collateral:
                return float(asset['availableBalance'])
            
    def place_market_order(self, pair: str, side: str, quantity: float) -> dict:
        try:
            order = self.client.futures_create_order(
                symbol=pair,
                side=side,
                type="MARKET",
                quantity=quantity
            )
            return order
        except Exception as e:
            logger.error(f'[ERROR] [{pair}] Exception while entering trade. Side: {side}')
            logger.exception(e)
    
    def place_limit_order(self, pair: str, side: str, quantity: float, price: float, reduce: bool = False
                          ) -> dict:
        try:
            order = self.client.futures_create_order(
                symbol=pair,
                side=side,
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce="GTC",
                reduceOnly=reduce
            )
            return order
        except Exception as e:
            logger.error(f'[ERROR] [{pair}] Exception while placing TP limit order')
            logger.exception(e)
            
    
    def place_stop_loss_order(self, pair: str, side: str, quantity: float, stop_price: float) -> dict:
        try:
            order = self.client.futures_create_order(
                symbol=pair,
                side=side,
                type="STOP_MARKET",
                quantity=quantity,
                stopPrice=stop_price,
                closePosition=True
            )
            return order
        except Exception as e:
            logger.error(f'[ERROR] [{pair}] Exception while placing SL order')
            logger.exception(e)
        
    def place_limit_tp_order(self, pair: str, side: str, quantity: float, price: float) -> dict:
        return self.place_limit_order(pair, side, quantity, price=price, reduce=True)
    
    def place_trailing_stop_order(self, pair: str, side: str, quantity: float, price: float, perc: float) -> dict:
        order = self.client.futures_create_order(
            symbol=pair,
            side=side,
            type="TRAILING_STOP_MARKET",
            quantity=quantity,
            price=price,
            timeInForce="GTC",
            reduceOnly=True,
            callbackRate=perc
        )
        return order

    def get_current_positions(self) -> dict:
        return self.client.futures_position_information()
    
    def cancel_order(self, symbol: str, order_id: str) -> bool:
        try:
            result = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            logger.debug(result)
            return result['status'] == 'CANCELED'
        except Exception as e:
            logger.error(f'[ERROR] [{symbol}] Exception while cancelling order')
            logger.exception(e)

    def get_open_orders(self, symbol: str):
        return self.client.futures_get_open_orders(symbol=symbol)
