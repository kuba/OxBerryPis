import zmq
from ..zhelpers import zpipe
import threading

from ...parsing.parsers import FileXDPChannelUnpacker as Unpacker

from .msgs_factories import StockMessagesFactory

from ..components import PubSubProxy
from ..components import SynchronizedPublisher


class StockMessagesPublisher(object):

    def __init__(self, context, uri, directory, channel_id):
        self.context = context
        self.uri = uri

        self.channel_id = channel_id

        self.unpacker = Unpacker.get_channel_unpacker(
            directory,
            channel_id,
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
            self.publisher.send_multipart(
                [stock_id, str(self.channel_id), serialized]
            )

        self.publisher.close()


def single_channel_parser_routine(context, proxy_uri, directory, channel):
    publisher = StockMessagesPublisher(
        context,
        proxy_uri,
        directory,
        channel
    )
    publisher.run()

def publishers_routine(pipe, context, publishers_uri, directory, channels_num):
    # Wait for signal
    pipe.recv()
    print "Received signal!"

    # Stock messages publishers threads
    for channel_id in xrange(1, channels_num + 1):
        thread = threading.Thread(
            target=single_channel_parser_routine,
            args=(context, publishers_uri, directory, channel_id,)
        )
        thread.daemon = True
        thread.start()

def controller_routine(pipe, context, publishers_uri, syncservice_uri,
        subscribers_expected):
    publisher = SynchronizedPublisher(
        context,
        publishers_uri,
        syncservice_uri,
        subscribers_expected,
    )
    publisher.setup()
    print '!!!'

    # Signal to publishers_routine
    pipe.send('')

def proxy_routine(context, frontend_uri, backend_uri):
    """Run a proxy"""
    proxy = PubSubProxy(context, frontend_uri, backend_uri)
    proxy.run()

if __name__ == '__main__':
    import sys

    if len(sys.argv) != 5:
        exit("USAGE: {0} controller_uri syncservice_uri subscribers_expected directory".format(sys.argv[0]))

    # Arguments
    controller_uri = sys.argv[1]
    syncservice_uri = sys.argv[2]
    subscribers_expected = int(sys.argv[3])
    directory = sys.argv[4]

    context = zmq.Context()
    publishers_uri = 'inproc://publishers'

    # Number of available channels
    channels_num = 4

    # Proxy thread
    proxy_thread = threading.Thread(
        target=proxy_routine,
        args=(context, publishers_uri, controller_uri,),
    )
    proxy_thread.daemon = True
    proxy_thread.start()

    pipe = zpipe(context)

    # Publishers thread
    publishers_thread = threading.Thread(
        target=publishers_routine,
        args=(
            pipe[0],
            context,
            publishers_uri,
            directory,
            channels_num,
        ),
    )
    publishers_thread.daemon = True
    publishers_thread.start()

    # Controller thread
    controller_thread = threading.Thread(
        target=controller_routine,
        args=(
            pipe[1],
            context,
            publishers_uri,
            syncservice_uri,
            subscribers_expected,
        ),
    )
    controller_thread.daemon = True
    controller_thread.start()

    while True:
        pass
