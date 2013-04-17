"""Parser for NYSE Arca Integrated Feed stream"""
import struct
import os.path

from oxberrypis.errors import OxBerryPisException

from oxberrypis.parsing.xdp import PacketHeader
from oxberrypis.parsing.xdp import MsgHeader


class ChannelParser(object):
    """ARCA Integrated Feed channel parser."""

    """Standard channel file name."""
    CHANNEL_FILE_NAME = "20111219-ARCA_XDP_IBF_{}.dat"

    def get_channel_path(self, directory, channel):
        """Get path to the channel found in the directory."""
        file_name = self.CHANNEL_FILE_NAME.format(channel)
        path = os.path.join(directory, file_name)
        return path

    def _parse_cls_from_stream(self, cls, stream):
        """Read the stream and parse to create an instance of given class."""
        data = stream.read(cls.size)
        unpacked = struct.unpack(cls.fmt, data)
        parsed = cls._make(unpacked)
        return parsed

    def parse_msg(self, header, stream):
        """Parse a single message."""
        msg_cls = header.get_msg_cls()
        msg = self._parse_cls_from_stream(msg_cls, stream)
        return msg

    def parse_packet(self, pkt_header, stream):
        """Parse a single packet."""
        count = pkt_header.NumberMsgs

        while count > 0:
            header = self._parse_cls_from_stream(MsgHeader, stream)

            if header.is_known():
                msg = self.parse_msg(header, stream)
                yield msg

            count -= 1

    def parse_file(self, file_name):
        """Parse channel file."""
        with open(file_name, 'rb') as channel_file:
            while True:
                pkt_header = self._parse_cls_from_stream(
                    PacketHeader,
                    channel_file
                )

                msgs = self.parse_packet(pkt_header, channel_file)
                for msg in msgs:
                    yield (pkt_header, msg)

    def parse_channel(self, directory, channel_id):
        """Find channel file and parse it."""
        channel_path = self.get_channel_path(directory, channel_id)

        if not os.path.exists(channel_path):
            raise OxBerryPisException(
                "Channel {} not found".format(channel_path)
            )

        packets = self.parse_file(channel_path)
        return packets

def main():
    import sys

    if len(sys.argv) != 3:
        exit("USAGE: {} directory channel".format(sys.argv[0]))

    directory = sys.argv[1]
    channel = sys.argv[2]

    cp = ChannelParser()

    for (pkt_header, msg) in cp.parse_channel(directory, channel):
        print msg

if __name__ == '__main__':
    main()
