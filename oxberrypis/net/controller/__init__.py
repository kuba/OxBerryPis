"""Network controller."""
from ..zhelpers import zpipe

from .init import InitializerThread

from .publisher import ProxyThread
from .publisher import ChannelPublishersThread


class Controller(object):
    """Network controller.

    The controller starts 3 threads:

    * :py:class:`.ProxyThread`
    * :py:class:`.InitializerThread`
    * :py:class:`.ChannelPublishersThread`


    :param context: ZMQ context.
    :param vissync_uri: ZMQ URI for syncing with the visualisation.
    :param rpisync_uri: ZMQ URI for syncing with RaspberryPis.
    :param pub_uri: ZMQ URI controller publishes from.

    :param subscribers_expected: Number of subscribers expected to connect
                                 to the controller before publishing starts.
    :type subscribers_expected: integer

    :param directory: Directory for NYSE ARCA Integrated Feed channel and
                      symbol index mapping files.
    :type directory: string

    :param channels_num: Number of channels to be processed.
    :type channels_num: integer

    :param mapping: symbol index mapping

    """
    def __init__(self, context, vissync_uri, rpisync_uri,
            pub_uri, subscribers_expected,
            directory, channels_num, mapping):
        # Proxy thread
        proxy_uri = 'inproc://channel-publishers'
        self.proxy_thread = ProxyThread(
            context,
            proxy_uri,
            pub_uri,
        )
        self.proxy_thread.daemon = True

        # Pipe for syncing Initializer and ChannelPublishers threads.
        pipe = zpipe(context)

        # Initializer thread
        self.initializer_thread = InitializerThread(
            context,
            vissync_uri,
            rpisync_uri,
            proxy_uri,
            pipe[0],
            subscribers_expected,
            mapping,
        )
        self.initializer_thread.daemon = True

        # Publishers thread
        self.publishers_thread = ChannelPublishersThread(
            context,
            pipe[1],
            proxy_uri,
            directory,
            channels_num,
        )
        self.publishers_thread.daemon = True

    def run(self):
        """Run the controller.

        Starts all subthreads and loop forever.

        """
        self.proxy_thread.start()
        self.initializer_thread.start()
        self.publishers_thread.start()

        while True:
            pass
