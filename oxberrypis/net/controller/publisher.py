import zmq

from ...parsing.parsers import FileXDPChannelUnpacker as Unpacker

from .msgs_factories import StockMessagesFactory


class StockMessagesPublisher(object):

    def __init__(self, context, uri, directory, channel):
        self.context = context

        self.publisher = context.socket(zmq.PUB)
        self.publisher.connect(uri)

        self.channel = channel

        self.unpacker = Unpacker.get_channel_unpacker(
            directory,
            channel,
        )

        self.factory = StockMessagesFactory()

    def run(self):
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


if __name__ == '__main__':
    import sys

    context = zmq.Context()

    uri = 'tcp://localhost:1234'

    if len(sys.argv) != 3:
        exit("USAGE: {0} directory channel".format(sys.argv[0]))

    directory = sys.argv[1]
    channel = int(sys.argv[2])

    c = StockMessagesPublisher(context, uri, directory, channel)
    c.run()
