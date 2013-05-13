"""Main script to be run on the controller computer."""
import sys
import os.path

import zmq

from ..net.controller import Controller

from ..parsing.symbols import parse_symbol_mapping_file
from ..parsing.symbols import SYMBOL_MAPPING_FILENAME


def get_mapping(directory):
    path = os.path.join(directory, SYMBOL_MAPPING_FILENAME)
    with open(path, 'r') as symbol_mapping_file:
        mapping_gen = parse_symbol_mapping_file(symbol_mapping_file)
        mapping = list(mapping_gen)

    return mapping

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

    mapping = get_mapping(directory)

    controller = Controller(
        context,
        vissync_uri,
        rpisync_uri,
        pub_uri,
        subscribers_expected,
        directory,
        channels_num,
        mapping,
    )
    controller.run()

if __name__ == '__main__':
    main()
