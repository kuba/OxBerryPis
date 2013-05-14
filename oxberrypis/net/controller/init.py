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

    #. Wait for given number (:attr:`subscribers_expected`) of
       Raspberry Pis.

    #. For every Raspberry Pi connected send back range of symbol
       indexes. Each range is sent to two different Raspberry Pis
       to allow high availability.

    #. Once all Raspberry Pis are connected hand over to the
       :py:class:`.ChannelPublishersThread`.


    :param context: ZMQ context.
    :param vissync_uri: ZMQ URI for syncing with the visualisation.
    :param rpisync_uri: ZMQ URI for syncing with Raspberry Pis.
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

        self.subscribers_expected = subscribers_expected
        self.ranges = list(chunks(mapping, subscribers_expected))

        self.syncpub = SynchronizedPublisher(
            context,
            proxy_uri,
            rpisync_uri,
            subscribers_expected,
            self.create_setup_rpi_msg_serialized,
        )

    def create_setup_rpi_msg(self, pi_id):
        """Create :py:class:`SetupRPi` message."""
        assert pi_id >= 0 and pi_id < self.subscribers_expected

        count = len(self.ranges)
        range1 = self.ranges[pi_id]
        range2 = self.ranges[pi_id + 1 % count]

        setup_rpi = SetupRPi()

        for mapping in range1 + range2:
            symbol_index = mapping[1]
            setup_rpi.symbol_index.append(symbol_index)

        return setup_rpi

    def create_setup_rpi_msg_serialized(self, pi_id):
        """Create serialized :py:class:`SetupRPi` message."""
        setup_rpi = self.create_setup_rpi_msg(pi_id)
        return setup_rpi.SerializeToString()

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

        # Wait for RPis
        self.syncpub.sync()

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
