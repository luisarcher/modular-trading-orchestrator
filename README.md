# modular-trading-orchestrator
Plugin based highly modular trading bot

This is a draft...

This project is divided into:
- services
- exchanges
- strategies

the application should be agnostic on which services, exchanges and strategies exist.
Those should be configured in a perhaps? yaml file

the applications should "know" what services, exchanges and strategies to load from the config file

- services: Messages arrive at the application via Services. The plan is that those should be configurable in a plug and play manner. Any user should easily be able to create and attach his own service without much hassle.
I plan to include: Telegram, flask and keyboard for now

- exchanges: following the same premisse as services, any user should be able to "plug and play" any exchange they use. Just by creating an exchange class and configuration.

- strategies: This is mostly risk management for now really as I expect that the entry trade signal should come from services. See example below...

### Use case

The use case of this project is as follows:
The user setups the services thats under use and sends a message to this application via such service, e.g. "buy btc 80" which can be translated as "buy 80 usd of bitcoin on the default configured exchange"... yes, I expect that the exchange name could be passed from the message as well, but again, this application is highly modular so it allows any user to do his own decoding...
Where were we? Yes, receiving message and decoding... 

- Services and event bus: Once the service decodes the text message, it should place it on the application event bus as a json object, e.g., {'ticker': 'BTCUSDT', 'QTY': 80, 'side': 'BUY'}

- Command handler: the command handler will pick the order from the event_bus and will then redirect it to the corresponding exchange on the ExchangeRegistry.

- Exchange registry maintains an object pool of all the exchanges configured, once an order is received internally, it redirects it to the exchange and will constantly poll it for price action of the open positions. The resulting polling data is then broadcasted to all the ongoing trade objects

- Trade object: Trade object will be listening from the information about open positions and price action ob its corresponding trade. If a strategy is configured the Trade object will signal the exchange mediator class to close or reduce a given trade according to the strategy.

- Strategy: Strategies can be configured locally and one or more can be set by default. The price action will be redirected to the strategy that acts accordingly. It is planned that the strategy could be configured from the service message like "buy btc 80 -tsl 2.8 -e bybit" which translates to "buy 80 usd of bitcoin on bybit exchange and use the trailling stop risk method"


### TODO

- [ ] Pytests
- [ ] BaseExchangeMediator abstract class
- [ ] flask endpoint that returns a json of current ongoing trades. Use __repr__ and __str__
- [ ] CommandHandler
- [ ] ExchangeRegistry
- [ ] Define the config structure

- [ ] Proper logging rotation
- [ ] Github semantic releases
- [ ] Write a proper readme and documentation
- [ ] Configure web3 exchanges
- [ ] Pydantic??
- [ ] ...


That's about it, and remember, this readme is an absolute draft

## Commands

keyboard: "quit" - gracefully terminates all services and the application.