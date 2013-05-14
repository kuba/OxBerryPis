"""Raspberry Pi stock messages subscriber/handler."""
import zmq

from ..components import SynchronizedSubscriber

from ..proto.stock_pb2 import StockMessage
from ..proto.controller_pb2 import SetupRPi

from ...orderbook.matching_engine import MatchingEngine

from .handlers import PrintingHandler
from .handlers import ToVisualisation
from .handlers import UpdateMatchingEngines


class StockMessagesSubscriber(object):
    """Stock messages subscriber.

    :param context: ZMQ context.
    :param rpisync_uri: ZMQ URI for syncing with the :py:class:`.Initializer`
    :param pub_uri: ZMQ URI for stock messages publisher.
    :param visual_uri: ZMQ URI visualisation binds to.
    :param me_handler_cls: Handler class for updating matching engines.
    :param visual_handler_cls: Handler class for sending stock events to
                               visualisation.

    """
    def __init__(self, context, rpisync_uri, pub_uri, visual_uri,
                 me_handler_cls=UpdateMatchingEngines,
                 visual_handler_cls=ToVisualisation):
        self.matching_engines = {}

        printing_handler = PrintingHandler()
        ordebook_handler = me_handler_cls(self.matching_engines)
        visual_handler = visual_handler_cls(
            self.matching_engines,
            context,
            visual_uri,
        )

        self.handlers = [
            printing_handler,
            ordebook_handler,
            visual_handler,
        ]

        # For the time being we don't know what to subscribe to.
        # We will resubscribe in sync_reply_handler
        subscriptions = []

        self.sub = SynchronizedSubscriber(
            context,
            pub_uri,
            rpisync_uri,
            subscriptions,
            self.handle_data,
            self.sync_reply_handler,
        )

    def sync_reply_handler(self, data):
        """Handler for synchronization reply message."""
        setup_rpi = SetupRPi()
        setup_rpi.ParseFromString(data)

        for symbol_index in setup_rpi.symbol_index:
            self.matching_engines[symbol_index] = MatchingEngine()

            # 2^32 (max SymbolIndex) is 10-digit number
            prefix = str(symbol_index).zfill(10)

            self.sub.subscribe(prefix)

    def run(self):
        """Run the subscriber."""
        self.sub.sync()
        self.sub.recv_multipart()

    def handle_data(self, data):
        """Handle subscribed data."""
        symbol_index, channel_id, serialized_stock_msg = data
        symbol_index = int(symbol_index)
        channel_id = int(channel_id)

        stock_msg = StockMessage()
        stock_msg.ParseFromString(serialized_stock_msg)

        for handler in self.handlers:
            handler.handle_stock_data(symbol_index, channel_id, stock_msg)
