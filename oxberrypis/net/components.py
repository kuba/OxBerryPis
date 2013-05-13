"""Reusable network components."""
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

    This publisher and :py:class:`SynchronizedSubscriber` are generally
    based on http://zguide.zeromq.org/py:all#Node-Coordination. However
    docs notes that:

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

    Therefore we implement above mentioned "more robust model", basin on
    http://thisthread.blogspot.co.uk/2012/03/pub-sub-coordination-by-req-rep.html.

    :param context: ZMQ context.
    :param publisher_uri: ZMQ URI the publisher binds to.
    :param syncservice_uri: ZMQ URI for publisher's syncing service REP socket.
    :param subscribers_expected: Number of expected subscribers.
    :param sync_reply: Synchronization reply function.
    :type sync_reply: function accepting sub_id and returning sync reply message.

    """
    PING_MSG = 'PING'
    END_MSG = 'END'

    def __init__(self, context, publisher_uri, syncservice_uri,
            subscribers_expected=1, sync_reply=None):
        self.context = context

        self.subscribers_expected = subscribers_expected

        self.publisher_uri = publisher_uri
        self.syncservice_uri = syncservice_uri

        # Socket to talk to clients
        self.publisher = self.context.socket(zmq.PUB)
        # Normally, we should bind, but in OxBerryPis
        # we connect to the pub-sub proxy
        #self.publisher.bind(self.publisher_uri)
        self.publisher.connect(self.publisher_uri)

        # Socket to receive signals
        self.syncservice = self.context.socket(zmq.REP)
        self.syncservice.bind(self.syncservice_uri)

        self.sync_reply = sync_reply or (lambda id: '')

    def sync(self):
        """Synchronize with subscribers."""
        # Get synchronization from subscribers
        subscribers = 0
        while subscribers < self.subscribers_expected:
            self.ping()
            if self.handshake(subscribers):
                subscribers += 1

    def ping(self):
        """Broadcast a ping message.

        A "ping" message is sent on the PUB socket to show the
        subscribers that the publisher is up and waiting for them.

        Sends :attr:`PING_MSG`.

        """
        self.publish(self.PING_MSG)

    def handshake(self, sub_id):
        """Perform handshake with subscriber if available.

        This function checks for subscribers synchronization
        on the REP socket.

        :param sub_id: Subscriber-to-be id.

        """
        # Sleep one second, to give time to the subscribers to connect.
        time.sleep(1)

        # Check on the socket for an empty message.
        try:
            msg = self.syncservice.recv(zmq.DONTWAIT)
        except zmq.ZMQError:
            return False

        # send synchronization reply
        reply = self.sync_reply(sub_id)
        self.syncservice.send(reply)

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
        """Announce end of publisher stream and close internal sockets.

        Sends :attr:`END_MSG`.

        """
        self.publish(self.END_MSG)
        self.publisher.close()


class SynchronizedSubscriber(object):
    """Synchronized subscriber.

    .. seealso:: Check :py:class:`SynchronizedPublisher` for
                 implementation details.

    :param context: ZMQ context.
    :param publisher_uri: ZMQ URI of the publisher.
    :param syncservice_uri: ZMQ URI of the publisher's REP socket for syncing.
    :param subscriptions: A list of prefixes to subscribe to.
    :param msg_handler: Function for handling of subscribed data.
    :param sync_reply_handler: Function for handling synchronization reply.

    """
    def __init__(self, context, publisher_uri, syncservice_uri,
            subscriptions, msg_handler, sync_reply_handler=None):
        self.context = context
        self.publisher_uri = publisher_uri
        self.syncservice_uri = syncservice_uri
        self.subscriptions = subscriptions
        self.msg_handler = msg_handler
        self.sync_reply_handler = sync_reply_handler or (lambda _: None)

        # First, connect our subscriber socket
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(self.publisher_uri)

        self.subscribe(SynchronizedPublisher.PING_MSG)
        self.subscribe(SynchronizedPublisher.END_MSG)

        for subscription in self.subscriptions:
            self.subscribe(subscription)

    def subscribe(self, subscription):
        """Subscribe to ``subscription``."""
        self.subscriber.setsockopt(zmq.SUBSCRIBE, subscription)

    def unsubscribe(self, subscription):
        """Unsubscribe from ``subscription``."""
        self.subscriber.setsockopt(zmq.UNSUBSCRIBE, subscription)

    def sync(self):
        """Synchronize with the publisher."""
        # Wait for dummy data from the SychronizedPublisher
        data = self.subscriber.recv()

        # Second, synchronize with publisher
        self.syncclient = self.context.socket(zmq.REQ)
        self.syncclient.connect(self.syncservice_uri)

        # send a synchronization request
        self.syncclient.send('')

        # wait for synchronization reply
        sync_reply = self.syncclient.recv()
        self.sync_reply_handler(sync_reply)

        self.unsubscribe(SynchronizedPublisher.PING_MSG)

    def recv(self):
        """Receive messages and proccess them using :attr:`msg_handler`
        in a loop.

        Stops when :py:attr:`SynchronizedPublisher.END_MSG` is received.

        """
        while True:
            data = self.subscriber.recv()
            if data == SynchronizedPublisher.END_MSG:
                break
            self.msg_handler(data)

    def recv_multipart(self):
        """Receive mulitpart messages and process them using
        :attr:`msg_handler` in a loop.

        Stops when :py:attr:`SynchronizedPublisher.END_MSG` is received.

        To be used with pub-sub message envelopes; based on
        http://zguide.zeromq.org/py:all#Pub-Sub-Message-Envelopes

        """
        # Third, get our updates and report how many we got
        while True:
            data = self.subscriber.recv_multipart()
            if data[0] == SynchronizedPublisher.END_MSG:
                break
            self.msg_handler(data)

    def close(self):
        """Close internal sockets."""
        self.syncclient.close()
        self.subscriber.close()
