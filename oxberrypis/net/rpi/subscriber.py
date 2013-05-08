"""Network communcation happening at RaspberryPi."""
import zmq

from ..proto.stock_pb2 import StockMessage

from ...orderbook.order import Order
from ...orderbook.book import OrderBook


class StockMessagesSubscriber(object):

    def __init__(self, context, publisher_uri, orderbooks):
        self.publisher_uri = publisher_uri
        self.stocks = stocks

        self.handler = StockMessagesToOrderbook(orderbooks)

        self.subscriber = context.socket(zmq.SUB)
        self.subscriber.connect(self.publisher_uri)

        for stock in self.stocks:
            stock_id = str(stock)
            self.subscriber.setsockopt(zmq.SUBSCRIBE, stock_id)

    def run(self):
        while True:
            symbol_index, data = self.subscriber.recv_multipart()
            stock_msg = StockMessage()
            stock_msg.ParseFromString(data)
            print stock_msg
            self.handler.handle_stock_message(stock_msg)


class StockMessagesToOrderbook(object):
    """Stock messages handler."""

    def __init__(self, orderbooks):
        self.orderbooks = orderbooks

    def handle_stock_message(self, message):
        """Update appropriate order book based on a stock ``message``."""
        if message.type == StockMessage.ADD:
            add_msg = message.add

            stock_id = add_msg.symbol_index
            order_id = add_msg.order_id
            limit_price = add_msg.price
            num_shares = add_msg.volume

            if add_msg.side == add_msg.BUY:
                side = Order.BUY
            else:
                side = Order.SELL

            order = Order(
                order_id,
                limit_price,
                num_shares,
                side,
            )

            self.orderbooks[stock_id].add_order(order)

            return stock_id
        elif message.type == StockMessage.MODIFY:
            modify_msg = message.modify

            stock_id = modify_msg.symbol_index
            order_id = modify_msg.order_id
            limit_price = modify_msg.price
            num_shares = modify_msg.volume

            if modify_msg.side == modify_msg.BUY:
                side = Order.BUY
            else:
                side = Order.SELL

            order = Order(
                order_id,
                limit_price,
                num_shares,
                side,
            )

            self.orderbooks[stock_id].update_order(order)

            return stock_id
        elif message.type == StockMessage.DELETE:
            delete_msg = message.delete

            stock_id = delete_msg.symbol_index
            order_id = delete_msg.order_id

            if delete_msg.side == delete_msg.BUY:
                side = Order.BUY
            else:
                side = Order.SELL

            self.orderbooks[stock_id].remove_order(order_id)

            return stock_id
        elif message.type == StockMessage.EXECUTE:
            exec_msg = message.execution

            stock_id = exec_msg.symbol_index
            order_id = exec_msg.order_id

            limit_price = exec_msg.price
            num_shares = exec_msg.volume

            orderbook = orderbooks[stock_id]
            if exec_msg.reason_code == exec_msg.FILLED:
                self.orderbook.remove_order(order_id)
            elif exec_msg.reason_code == exec_msg.PARTIAL:
                self.orderbook.decrease_order_amount_by(
                    order_id,
                    num_shares,
                )
            else:
                #  otherwise do nothing (this type of message may be useless)
                pass

            return stock_id
        elif message.type == StockMessage.TRADE:
            trade_msg = message.trade

            stock_id = trade_msg.symbol_index
            return stock_id
        else:
            raise OxBerryPisExecption("Invalid Message Type")


if __name__ == '__main__':
   context = zmq.Context()
   publisher_uri = 'tcp://127.0.0.1:2001'

   stocks = xrange(1, 50000)
   orderbooks = {}
   for stock in stocks:
       orderbooks[stock] = OrderBook()

   subscriber = StockMessagesSubscriber(
        context,
        publisher_uri,
        orderbooks,
    )
   subscriber.run()
