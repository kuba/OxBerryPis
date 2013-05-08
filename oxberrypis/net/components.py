import zmq
import time


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


class SynchronizedPublisher(object):
    """Synchronized publisher.

    Based on http://zguide.zeromq.org/py:all#Node-Coordination

    We can't assume that the SUB connect will be finished by the time
    the REQ/REP dialog is complete. There are no guarantees that
    outbound connects will finish in any order whatsoever, if you're
    using any transport except inproc. So, the example does a brute
    force sleep of one second between subscribing, and sending the
    REQ/REP synchronization.

    A more robust model could be:

    * Publisher opens PUB socket and starts sending "Hello"
      messages (not data).
    * Subscribers connect SUB socket and when they receive a
      Hello message they tell the publisher via a REQ/REP
      socket pair.
    * When the publisher has had all the necessary
      confirmations, it starts to send real data.

    http://thisthread.blogspot.co.uk/2012/03/pub-sub-coordination-by-req-rep.html


    """
    PING_MSG = 'PING'
    END_MSG = 'END'

    def __init__(self, context, publisher_uri, syncservice_uri,
            subscribers_expected=1):
        self.context = context

        self.subscribers_expected = subscribers_expected

        self.publisher_uri = publisher_uri
        self.syncservice_uri = syncservice_uri

        # Socket to talk to clients
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.connect(self.publisher_uri)

        # Socket to receive signals
        self.syncservice = self.context.socket(zmq.REP)
        self.syncservice.bind(self.syncservice_uri)

    def setup(self):
        # Get synchronization from subscribers
        subscribers = 0
        while subscribers < self.subscribers_expected:
            self.ping()
            if self.handshake():
                subscribers += 1

    def ping(self):
        """Broadcast a ping message.

        A "ping" message is sent on the PUB socket to show the
        subscribers that the publisher is up and waiting for them.

        """
        self.publish(self.PING_MSG)

    def handshake(self):
        """Perform handshake with subscriber if available.

        This function checks for subscribers synchronization
        on the REP socket.

        """
        # Sleep one second, to give time to the subscribers to connect.
        time.sleep(1)

        # Check on the socket for an empty message.
        try:
            msg = self.syncservice.recv(zmq.DONTWAIT)
        except zmq.ZMQError:
            return False

        # send synchronization reply
        self.syncservice.send('')

        return True

    def publish(self, data):
        """Send data to subscribers."""
        self.publisher.send(data)

    def publish_enveloped(self, key, data):
        """Send enveloped data to subscribers.

        Based on http://zguide.zeromq.org/py:all#Pub-Sub-Message-Envelopes

        """
        self.publisher.send_mulipart([key, data])

    def close(self):
        self.publish(self.END_MSG)
        self.publisher.close()


class DummyMsgHandler(object):
    def received(sellf, msg):
        print msg


class SynchronizedSubscriber(object):
    """Synchronized subscriber.

    Based on http://zguide.zeromq.org/py:all#Node-Coordination.

    """
    def __init__(self, context, publisher_uri, syncservice_uri, subscriptions, msg_handler):
        self.context = context
        self.publisher_uri = publisher_uri
        self.syncservice_uri = syncservice_uri
        self.subscriptions = subscriptions
        self.msg_handler = msg_handler

        # First, connect our subscriber socket
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(self.publisher_uri)

        self.subscriber.setsockopt(zmq.SUBSCRIBE, SynchronizedPublisher.PING_MSG)
        self.subscriber.setsockopt(zmq.SUBSCRIBE, SynchronizedPublisher.END_MSG)

        for subscription in self.subscriptions:
            self.subscriber.setsockopt(zmq.SUBSCRIBE, subscription)

    def setup(self):
        data = self.subscriber.recv()

        # Second, synchronize with publisher
        self.syncclient = self.context.socket(zmq.REQ)
        self.syncclient.connect(self.syncservice_uri)

        # send a synchronization request
        self.syncclient.send('')

        # wait for synchronization reply
        self.syncclient.recv()

        self.subscriber.setsockopt(zmq.UNSUBSCRIBE, SynchronizedPublisher.PING_MSG)

    def recv(self):
        # Third, get our updates and report how many we got
        while True:
            data = self.subscriber.recv()
            if data == SynchronizedPublisher.END_MSG:
                break
            self.msg_handler(data)

    def recv_multipart(self):
        """To be used with pub-sub message envelopes.

        Based on http://zguide.zeromq.org/py:all#Pub-Sub-Message-Envelopes

        """
        # Third, get our updates and report how many we got
        while True:
            data = self.subscriber.recv_multipart()
            if data[0] == SynchronizedPublisher.END_MSG:
                break
            self.msg_handler(data)
