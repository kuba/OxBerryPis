"""Network communcation happening at RaspberryPi."""
import zmq

from ..components import SynchronizedSubscriber

from ..proto.stock_pb2 import StockMessage

from ...orderbook.order import Order
from ...orderbook.book import OrderBook

class ToVisualisation(object):
    """ Send stock messages to visualisation"""


    def _init_(self,matching_engines,visual_uri,context):
        self.matching_engines = matching_engines
        self.to_visualisation = context.socket(zmq.PUSH)
        self.to_visualisation.connect(visualisation_uri)
        self.last_top_buy = {}
        self.last_top_sell = {}


    def make_price_message(self,message,stock_id,stream_id):
        """Makes the message to send to visualisation."""
        
        matching_engine = matching_engines[stock_id]
        
        top_sell_price, top_buy_price = matching_engine.get_best_orders()

        if (message.type != StockMessage.TRADE and 
            stock_id in last_top_buy and 
            stock_id in last_top_sell and 
            last_top_buy[stock_id] == top_buy_price and 
            last_top_sell[stock_id] == top_sell_price):
            return None

        last_top_buy[stock_id] = top_buy_price
        last_top_sell[stock_id] = top_sell_price

        event = StockEvent()
        event.stock_id = stock_id
        event.timestamp_s = message.timestamp_s
        event.timestamp_ns = message.timestamp_ns
        event.stream_id = stream_id
        
        if message.type == StockMessage.TRADE:
            visual_msg.last_trade_price = message.trade.price
            
        

        if top_buy_price is not None:
            event.top_buy_price = top_buy_price
        if top_sell_price is not None:
            top_sell_price = top_sell_price
        return true,event
        
    def handle_send_visual(self,message,stock_id):
        """Handle sending a single stock event to visualisation"""
        visual_msg = self.make_price_message(message,stock_id,stream_id)
        if (visual_msg is not None):
            self.to_visualisation.send(msg.serialize_to_string())






    

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

class StockMessagesSubscriber(object):

    def __init__(self, context, publisher_uri, syncservice_uri,visual_uri,
                 stock_handler_cls=StockMessagesToOrderbook,
                 visual_handler_cls=ToVisualisation):
        stocks = xrange(1, 50000)

        orderbooks = {}
        for stock in stocks:
            orderbooks[stock] = OrderBook()

        self.stock_handler = stock_handler_cls(orderbooks)
        self.visual_handler = visual_handler_cls(orderbooks,visual_uri,context)
        subscriptions = map(str, stocks)

        self.sub = SynchronizedSubscriber(
            context,
            publisher_uri,
            syncservice_uri,
            subscriptions,
            self.handle_data,
        )

    def run(self):
        self.sub.setup()
        self.sub.recv_multipart()

    def handle_data(self, data):
        symbol_index, serialized_stock_msg = data
       
        # Using dummy stream_id for now
        stream_id = 0
        
        stock_msg = StockMessage()
        stock_msg.ParseFromString(serialized_stock_msg)
        print stock_msg
        stock_id = self.stock_handler.handle_stock_message(stock_msg)
        self.visual_handler.send_to_visual(stock_msg,stock_id,stream_id)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        exit("USAGE: {} publisher_uri syncservice_uri visual_uri".format(sys.argv[0]))

    publisher_uri = sys.argv[1]
    syncservice_uri = sys.argv[2]
    visual_uri = sys.argv[3]

    context = zmq.Context()

    sub = StockMessagesSubscriber(
        context,
        publisher_uri,
        syncservice_uri,
        visual_uri
    )
    
    sub.run()
