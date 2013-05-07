import sys

from ..parsing.parsers import FileXDPChannelUnpacker
from ..parsing.messages import *

def channel_parser():
    if len(sys.argv) != 3:
        exit("USAGE: {} directory channel".format(sys.argv[0]))

    directory = sys.argv[1]
    channel = sys.argv[2]

    unpacker = FileXDPChannelUnpacker.get_channel_unpacker(directory, channel)

    for (pkt_header, msg) in unpacker.parse():
        pkt_time = pkt_header.get_datetime()
        print pkt_time, msg
