"""Network communcation happening at RaspberryPi."""
import zmq

from ..components import SynchronizedSubscriber

from ..proto.stock_pb2 import StockMessage

from ...orderbook.matching_engine import MatchingEngine

from .handlers import ToVisualisation
from .handlers import StockMessagesToOrderbook


class StockMessagesSubscriber(object):

    def __init__(self, context, publisher_uri, syncservice_uri,visual_uri,
                 stock_handler_cls=StockMessagesToOrderbook,
                 visual_handler_cls=ToVisualisation):
        stocks = xrange(1, 50000)

        matching_engines = {}
        for stock in stocks:
            matching_engines[stock] = MatchingEngine()

        self.stock_handler = stock_handler_cls(matching_engines)
        self.visual_handler = visual_handler_cls(matching_engines, visual_uri, context)
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
        symbol_index, channel_id, serialized_stock_msg = data
        channel_id = int(channel_id)

        stock_msg = StockMessage()
        stock_msg.ParseFromString(serialized_stock_msg)
        print stock_msg
        stock_id = self.stock_handler.handle_stock_message(stock_msg)
        self.visual_handler.handle_send_visual(stock_id, channel_id, stock_msg)
