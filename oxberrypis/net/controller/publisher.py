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


def single_channel_parser_routine(context, proxy_uri, directory, channel):
    publisher = StockMessagesPublisher(
        context,
        proxy_uri,
        directory,
        channel
    )
    publisher.run()

def proxy_routine(context, frontend_uri, backend_uri):
    """Run a proxy"""
    proxy = PubSubProxy(context, frontend_uri, backend_uri)
    proxy.run()

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 4:
        exit("USAGE: {0} ip port directory".format(sys.argv[0]))

    # Arguments
    ip = sys.argv[1]
    port = sys.argv[2]
    directory = sys.argv[3]

    context = zmq.Context()
    publishers_uri = 'inproc://publishers'
    publisher_uri = 'tcp://{}:{}'.format(ip, port)

    # Number of available channels
    channels_num = 4

    # Proxy thread
    proxy_thread = threading.Thread(
        target=proxy_routine,
        args=(context, publishers_uri, publisher_uri,),
    )
    proxy_thread.daemon = True
    proxy_thread.start()

    # Stock messages publishers threads
    for channel_id in xrange(1, channels_num + 1):
        thread = threading.Thread(
            target=single_channel_parser_routine,
            args=(context, publishers_uri, directory, channel_id,)
        )
        thread.daemon = True
        thread.start()

    while True:
        pass
