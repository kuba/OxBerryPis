import zmq
import threading

from ...parsing.parsers import FileXDPChannelUnpacker as Unpacker

from .msgs_factories import StockMessagesFactory

from ..components import PubSubProxy


class StockMessagesPublisher(object):

    def __init__(self, context, uri, directory, channel):
        self.context = context
        self.uri = uri

        self.unpacker = Unpacker.get_channel_unpacker(
            directory,
            channel,
        )

        self.factory = StockMessagesFactory()

    def run(self):
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(self.uri)

        for (pkt_hdr, msg) in self.unpacker.parse():
            stock_msg = self.factory.create(pkt_hdr, msg)

            # Ignore messages with no handler in the factory
            if stock_msg is None:
                continue

            # Ignore messages without symbol index
            if not hasattr(msg, 'SymbolIndex'):
                continue

            stock_id = str(msg.SymbolIndex)
            serialized = stock_msg.SerializeToString()
            self.publisher.send_multipart([stock_id, serialized])

        self.publisher.close()


def worker_routine(context, uri, directory, channel):
    publisher = StockMessagesPublisher(
        context,
        uri,
        directory,
        channel
    )
    publisher.run()


if __name__ == '__main__':
    import sys

    context = zmq.Context()

    frontend_uri = 'tcp://127.0.0.1:2000'
    backend_uri = 'tcp://127.0.0.1:2001'

    proxy = PubSubProxy(context, frontend_uri, backend_uri)

    if len(sys.argv) != 2:
        exit("USAGE: {0} directory".format(sys.argv[0]))

    directory = sys.argv[1]

    for channel_id in xrange(1, 5):
        thread = threading.Thread(
            target=worker_routine,
            args=(context, frontend_uri, directory, channel_id,)
        )
        thread.start()

    proxy.run()
