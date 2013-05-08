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

class Publisher(object):

    def __init__(self, context, publishers_uri, controller_uri, syncservice_uri,
            subscribers_expected, directory, channels_num):
        self.context = context
        self.publishers_uri = publishers_uri
        self.controller_uri = controller_uri
        self.syncservice_uri = syncservice_uri
        self.subscribers_expected = subscribers_expected
        self.directory = directory
        self.channels_num = channels_num

    def run(self):
        # Proxy thread
        proxy_thread = threading.Thread(
            target=proxy_routine,
            args=(
                self.context,
                self.publishers_uri,
                self.controller_uri,
            ),
        )
        proxy_thread.daemon = True
        proxy_thread.start()

        pipe = zpipe(self.context)

        # Publishers thread
        publishers_thread = threading.Thread(
            target=publishers_routine,
            args=(
                pipe[0],
                self.context,
                self.publishers_uri,
                self.directory,
                self.channels_num,
            ),
        )
        publishers_thread.daemon = True
        publishers_thread.start()

        # Controller thread
        controller_thread = threading.Thread(
            target=controller_routine,
            args=(
                pipe[1],
                self.context,
                self.publishers_uri,
                self.syncservice_uri,
                self.subscribers_expected,
            ),
        )
        controller_thread.daemon = True
        controller_thread.start()

        while True:
            pass
