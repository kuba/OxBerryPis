"""Main script to be run on the controller computer."""
import sys
import zmq
from ..net.controller import Controller


def main():
    """Run main controller."""
    if len(sys.argv) != 6:
        exit("USAGE: {0} vissync_uri rpisync_uri pub_uri subscribers_expected directory".format(sys.argv[0]))

    # Arguments
    vissync_uri = sys.argv[1]
    rpisync_uri = sys.argv[2]
    pub_uri = sys.argv[3]
    subscribers_expected = int(sys.argv[4])
    directory = sys.argv[5]

    context = zmq.Context()

    # Number of available channels
    channels_num = 4

    controller = Controller(
        context,
        vissync_uri,
        rpisync_uri,
        pub_uri,
        subscribers_expected,
        directory,
        channels_num,
    )
    controller.run()

if __name__ == '__main__':
    main()
