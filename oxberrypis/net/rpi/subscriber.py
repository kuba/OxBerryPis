"""Network communcation happening at RaspberryPi."""
import zmq

from ..components import SynchronizedSubscriber

from ..proto.stock_pb2 import StockMessage
from ..proto.controller_pb2 import SetupRPi

from ...orderbook.matching_engine import MatchingEngine

from .handlers import ToVisualisation
from .handlers import StockMessagesToOrderbook


class StockMessagesSubscriber(object):

    def __init__(self, context, publisher_uri, syncservice_uri,visual_uri,
                 stock_handler_cls=StockMessagesToOrderbook,
                 visual_handler_cls=ToVisualisation):
        self.matching_engines = {}

        self.stock_handler = stock_handler_cls(self.matching_engines)
        self.visual_handler = visual_handler_cls(
            self.matching_engines,
            visual_uri,
            context,
        )

        # For the time being we don't know what to subscribe to.
        # We will resubscribe in sync_reply_handler
        subscriptions = []

        self.sub = SynchronizedSubscriber(
            context,
            publisher_uri,
            syncservice_uri,
            subscriptions,
            self.handle_data,
            self.sync_reply_handler,
        )

    def sync_reply_handler(self, data):
        setup_rpi = SetupRPi()
        setup_rpi.ParseFromString(data)

        for symbol_index in setup_rpi.symbol_index:
            self.matching_engines[symbol_index] = MatchingEngine()

            # 2^32 (max SymbolIndex) is 10-digit number
            prefix = str(symbol_index).zfill(10)

            self.sub.subscribe(prefix)

    def run(self):
        self.sub.sync()
        self.sub.recv_multipart()

    def handle_data(self, data):
        symbol_index, channel_id, serialized_stock_msg = data
        channel_id = int(channel_id)

        stock_msg = StockMessage()
        stock_msg.ParseFromString(serialized_stock_msg)
        print stock_msg
        stock_id = self.stock_handler.handle_stock_message(stock_msg)
        self.visual_handler.handle_send_visual(stock_id, channel_id, stock_msg)
