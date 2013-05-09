"""Network communcation happening at RaspberryPi."""
import zmq

from ..components import SynchronizedSubscriber

from ..proto.stock_pb2 import StockMessage

from ...orderbook.matching_engine import MatchingEngine

from .handlers import ToVisualisation
from .handlers import StockMessagesToOrderbook


class StockMessagesSubscriber(object):

    def __init__(self, context, publisher_uri, syncservice_uri,visual_uri,
                 range0_start,range0_end,
                 range1_start,range1_end
                 stock_handler_cls=StockMessagesToOrderbook,
                 visual_handler_cls=ToVisualisation):
        stocks1 =  range(range0_start, range0_end) 
        stocks2 = range(range1_start, range1_end)
        stocks  = stocks1+ stocks2

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
        #self.visual_handler.handle_send_visual(stock_id, channel_id, stock_msg)

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 4:
        exit("USAGE: {} publisher_uri syncservice_uri visual_uri range0_start range0_end range1_start range1_end".format(sys.argv[0]))

    publisher_uri = sys.argv[1]
    syncservice_uri = sys.argv[2]
    visual_uri = sys.argv[3]

    context = zmq.Context()

    sub = StockMessagesSubscriber(
        context,
        publisher_uri,
        syncservice_uri,
        visual_uri,
        range0_start,
        range0_end,
        range1_start,
        range1_end

    )

    sub.run()
