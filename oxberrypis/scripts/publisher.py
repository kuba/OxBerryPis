"""Publisher script to be run on the controller computer."""
import sys
import zmq
from oxberrypis.net.controller.publisher import Publisher


def main():
    if len(sys.argv) != 5:
        exit("USAGE: {0} controller_uri syncservice_uri subscribers_expected directory".format(sys.argv[0]))

    # Arguments
    controller_uri = sys.argv[1]
    syncservice_uri = sys.argv[2]
    subscribers_expected = int(sys.argv[3])
    directory = sys.argv[4]

    context = zmq.Context()
    publishers_uri = 'inproc://publishers'

    # Number of available channels
    channels_num = 4

    publisher = Publisher(
        context,
        publishers_uri,
        controller_uri,
        syncservice_uri,
        subscribers_expected,
        directory,
        channels_num,
    )
    publisher.run()

if __name__ == '__main__':
    main()
