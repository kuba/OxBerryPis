"""Subscriber script to be run on RPis."""
import sys
import zmq
from oxberrypis.net.rpi.subscriber import StockMessagesSubscriber


def main():
    if len(sys.argv) != 4:
        exit("USAGE: {} publisher_uri syncservice_uri visual_uri".format(sys.argv[0]))

    publisher_uri = sys.argv[1]
    syncservice_uri = sys.argv[2]
    visual_uri = sys.argv[3]

    context = zmq.Context()

    sub = StockMessagesSubscriber(
        context,
        publisher_uri,
        syncservice_uri,
        visual_uri
    )

    sub.run()

if __name__ == '__main__':
    main()
