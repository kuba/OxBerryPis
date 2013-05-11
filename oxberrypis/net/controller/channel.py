"""Network components responsible for a single channel parsing/publishing."""
import threading

import zmq

from ...parsing.parsers import FileXDPChannelUnpacker as Unpacker
from .msgs_factories import StockMessagesFactory


class ChannelStockMsgsGenerator(object):
    """Stock messages generator from the channel.

    :param directory: Directory with NYSE Arca Integrated Feed
                      channels files.
    :type directory: string

    :param channel_id: Channel ID to be parsed.
    :type channel_id: integer

    :param factory: Factory for :py:class:`StockMessage` objects,
                    defaults to an instance of
                    :py:class:`StockMessagesFactory`.

    """
    def __init__(self, directory, channel_id, factory=None):
        self.unpacker = Unpacker.get_channel_unpacker(
            directory,
            channel_id,
        )
        self.factory = factory or StockMessagesFactory()

    def generate_stock_msgs(self):
        """Generate stock messages (with stock ids).

        Yields :py:class:`StockMessage` object for every known
        message found in the channel stream.

        """
        for (pkt_hdr, msg) in self.unpacker.parse():
            stock_msg = self.factory.create(pkt_hdr, msg)

            # Ignore messages with no handler in the factory
            if stock_msg is None:
                continue

            # Ignore messages without symbol index
            if not hasattr(msg, 'SymbolIndex'):
                continue

            stock_id = msg.SymbolIndex
            serialized = stock_msg.SerializeToString()
            yield stock_id, stock_msg


class ChannelPublisher(object):
    """Channel publisher.

    Parses a single channel and publishes :py:class:`StockMessage` messages.

    :param context: ZMQ context.
    :param uri: ZMQ URI publisher publishes to.
    :param directory: Directory with NYSE Arca Integrated Feed channels
                      files.
    :param channel_id: Channel ID to be parsed.
    :type channel_id: integer

    """
    def __init__(self, context, uri, directory, channel_id):
        # Setup a socket
        self.publisher = context.socket(zmq.PUB)
        self.publisher.connect(uri)

        self.channel_id = channel_id

        self.generator = ChannelStockMsgsGenerator(directory, channel_id)
        self.factory = StockMessagesFactory()

    def run(self):
        """Run the publisher."""
        for (stock_id, stock_msg) in self.generator.generate_stock_msgs():
            serialized = stock_msg.SerializeToString()

            self.publisher.send_multipart(
                [str(stock_id), str(self.channel_id), serialized]
            )

        self.publisher.close()


class ChannelPublisherThread(threading.Thread):
    """Channel publisher thread."""
    def __init__(self, context, uri, directory, channel_id, name=None):
        name = name or "ChannelPublisher{}".format(channel_id)
        super(ChannelPublisherThread, self).__init__(name=name)

        self.channel_publisher = ChannelPublisher(
            context,
            uri,
            directory,
            channel_id,
        )

    def run(self):
        """Run the thread."""
        self.channel_publisher.run()
