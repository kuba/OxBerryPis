"""Network initialization."""
import zmq
import threading

from ..components import SynchronizedPublisher


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

    """
    def __init__(self, context, vissync_uri, rpisync_uri, proxy_uri,
            to_publishers_pipe, subscribers_expected):
        self.vissync = context.socket(zmq.REP)
        self.vissync.bind(vissync_uri)

        self.to_publishers_pipe = to_publishers_pipe


        self.syncpub = SynchronizedPublisher(
            context,
            proxy_uri,
            rpisync_uri,
            subscribers_expected,
        )

    def run(self):
        """Run the initializer."""
        # TODO: wait for visualisation
        #setup_vis = SetupVisualisation()

        # Wait for signal from visualisation
        #self.vissync.read()
        #self.vissync.send(setup_vis)
        # Wait for acknowledgement
        #self.vissync.read()

        # Wait for RPis
        self.syncpub.setup()

        # Signal to ChannelPublishersThread
        self.to_publishers_pipe.send('')

class InitializerThread(threading.Thread):
    """:py:class:`Initializer` thread.

    .. seealso :: For constructor parameters check :py:class:`Initializer`.

    """
    def __init__(self, context, vissync_uri, rpisync_uri, proxy_uri,
            to_publishers_pipe, subscribers_expected, name="Initializer"):
        super(InitializerThread, self).__init__(name=name)

        self.initializer = Initializer(
            context,
            vissync_uri,
            rpisync_uri,
            proxy_uri,
            to_publishers_pipe,
            subscribers_expected,
        )

    def run(self):
        """Run the initializer thread."""
        self.initializer.run()
