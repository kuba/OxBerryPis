"""Network initialization."""
import zmq
import threading

from ...utils import chunks

from ..components import SynchronizedPublisher

from ..proto.controller_pb2 import SetupVisualisation
from ..proto.controller_pb2 import SetupRPi


class Initializer(object):
    """Network initializer.

    Initilizer works as following:

    #. Wait for visualisation.

    #. Once visualisation connects, send back ranges of symbol indexes
       which will be distributed over the RapsberryPis.

    #. Wait for acknowledgement from the visualisation.

    #. Wait for given number (:attr:`subscribers_expected`) of
       RaspberryPis.

    #. For every RaspberryPi connected send back range of symbol
       indexes. Each range is sent to two different RaspberryPis
       to allow high availability. Wait for acknowledgement.

    #. Once all RaspberryPis are connected hand over to the
       :py:class:`.ChannelPublishersThread`.


    :param context: ZMQ context.
    :param vissync_uri: ZMQ URI for syncing with the visualisation.
    :param rpisync_uri: ZMQ URI for syncing with RaspberryPis.
    :param proxy_uri: ZMQ URI for publishers proxy's frontend.
    :param to_publishers_pipe: Pipe used to sync :py:class:`Initializer`
                               with the :py:class:`.ChannelPublishersThread`.
    :param subscribers_expected: Number of subscribers expected to
                                 connect to the controller before
                                 publishing starts.
    :type subscribers_expected: integer
    :param mapping: List of symbol mappings.

    """
    def __init__(self, context, vissync_uri, rpisync_uri, proxy_uri,
            to_publishers_pipe, subscribers_expected, mapping):
        self.vissync = context.socket(zmq.REP)
        self.vissync.bind(vissync_uri)

        self.to_publishers_pipe = to_publishers_pipe

        self.ranges = list(chunks(mapping, subscribers_expected))

        self.syncpub = SynchronizedPublisher(
            context,
            proxy_uri,
            rpisync_uri,
            subscribers_expected,
        )

    def create_setup_visualisation_msg(self):
        """Create SetupVisualisation message."""
        setup_vis = SetupVisualisation()

        for index_range in self.ranges:
            current_range = setup_vis.range.add()
            for mapping in index_range:
                current_mapping = current_range.mapping.add()
                current_mapping.symbol = mapping[0]
                current_mapping.symbol_index = mapping[1]
                current_mapping.price_scale_code = mapping[2]

        return setup_vis

    def run(self):
        """Run the initializer."""
        setup_vis = self.create_setup_visualisation_msg()
        setup_vis_serialized = setup_vis.SerializeToString()

        # Wait for signal from visualisation
        self.vissync.recv()
        self.vissync.send(setup_vis_serialized)
        # Wait for acknowledgement
        self.vissync.recv()

        # Wait for RPis
        self.syncpub.setup()

        # Signal to ChannelPublishersThread
        self.to_publishers_pipe.send('')

class InitializerThread(threading.Thread):
    """:py:class:`Initializer` thread.

    .. seealso :: For constructor parameters check :py:class:`Initializer`.

    """
    def __init__(self, context, vissync_uri, rpisync_uri, proxy_uri,
            to_publishers_pipe, subscribers_expected, mapping,
            name="Initializer"):
        super(InitializerThread, self).__init__(name=name)

        self.initializer = Initializer(
            context,
            vissync_uri,
            rpisync_uri,
            proxy_uri,
            to_publishers_pipe,
            subscribers_expected,
            mapping,
        )

    def run(self):
        """Run the initializer thread."""
        self.initializer.run()
