import zmq


class PubSubProxy(object):
    """Publisher-Subscriber proxy.

    Based on:

    * http://zguide.zeromq.org/py:all#The-Dynamic-Discovery-Problem
    * http://zguide.zeromq.org/py:all#-MQ-s-Built-In-Proxy-Function

    """
    def __init__(self, context, frontend_uri, backend_uri):
        self.context = context
        self.frontend_uri = frontend_uri
        self.backend_uri = backend_uri

        # Socket facing clients
        self.frontend = self.context.socket(zmq.XSUB)
        self.frontend.bind(self.frontend_uri)

        # Socket facing services
        self.backend = self.context.socket(zmq.XPUB)
        self.backend.bind(self.backend_uri)

    def run(self):
        zmq.device(zmq.QUEUE, self.frontend, self.backend)

        # We never get here...
        self.frontend.close()
        self.backend.close()
