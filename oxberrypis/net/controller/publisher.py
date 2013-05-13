"""Network components responsible for publishing stock messages."""
import threading

from .channel import ChannelPublisherThread

from ..components import PubSubProxy


class ProxyThread(threading.Thread):
    """Pub-sub proxy thread.

    :param context: ZMQ context.
    :param frontend_uri: ZMQ URI proxy listens to.
    :param backend_uri: ZMQ URI proxy rebpublishes to.
    :param name: Name of the thread; useful for debugging.

    """
    def __init__(self, context, frontend_uri, backend_uri, name="Proxy"):
        super(ProxyThread, self).__init__(name=name)

        self.proxy = PubSubProxy(
            context,
            frontend_uri,
            backend_uri,
        )

    def run(self):
        """Run the proxy."""
        self.proxy.run()


class ChannelPublishersThread(threading.Thread):
    """Channel publishers thread.

    :param context: ZMQ context.
    :param init_pipe: Pipe used to sync with the :py:class:`Initializer`.
    :param proxy_uri: Destination channel publishers publish to.
    :param directory: Directory when channel files are found.
    :param channels_num: Number of channels to process. Parsing will
                         start with channel 1.
    :param name: Name of the thread; useful for debugging.

    """
    def __init__(self, context, init_pipe, proxy_uri, directory,
            channels_num, name="ChannelPublishers"):
        super(ChannelPublishersThread, self).__init__(name=name)

        self.init_pipe = init_pipe

        self.cp_threads = []
        for channel_id in xrange(1, channels_num + 1):
            cp_thread = ChannelPublisherThread(
                context,
                proxy_uri,
                directory,
                channel_id,
            )
            cp_thread.daemon = True

            self.cp_threads.append(cp_thread)

    def run(self):
        """Run the channel publishers thread."""
        # Wait for signal from initializer
        self.init_pipe.recv()

        for cp_thread in self.cp_threads:
            cp_thread.start()
