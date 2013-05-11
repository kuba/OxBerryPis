"""Main script to be run on RPis."""
import sys
import zmq
from ..net.rpi.subscriber import StockMessagesSubscriber


def main():
    """Run RPi stock messages subscriber."""
    if len(sys.argv) != 4:
        exit("USAGE: {} rpisync_uri pub_uri visual_uri".format(sys.argv[0]))

    rpisync_uri = sys.argv[1]
    pub_uri = sys.argv[2]
    visual_uri = sys.argv[3]

    context = zmq.Context()

    sub = StockMessagesSubscriber(
        context,
        pub_uri,
        rpisync_uri,
        visual_uri
    )

    sub.run()

if __name__ == '__main__':
    main()
