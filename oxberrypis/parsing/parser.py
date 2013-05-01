"""Parser for NYSE Arca Integrated Feed stream"""
import os
import struct
import os.path

from oxberrypis.errors import OxBerryPisException

from oxberrypis.parsing.xdp import PacketHeader
from oxberrypis.parsing.xdp import MsgHeader


class ChannelParser(object):
    """ARCA Integrated Feed channel parser."""

    """Standard channel file name."""
    CHANNEL_FILE_NAME = "20111219-ARCA_XDP_IBF_{}.dat"

    def _get_channel_path(self, channel_file_name, directory, channel):
        file_name = channel_file_name.format(channel)
        path = os.path.join(directory, file_name)
        return path

    def get_channel_path(self, directory, channel):
        """Get path to the channel found in the directory."""
        channel_file_name = self.CHANNEL_FILE_NAME
        return self._get_channel_path(channel_file_name, directory, channel)

    def _parse_cls_from_stream(self, cls, size, stream):
        """Read the stream and parse to create an instance of given class."""
        data = stream.read(size)
        unpacked = struct.unpack_from(cls.fmt, data)
        parsed = cls._make(unpacked)
        return parsed

    def parse_msg(self, header, stream):
        """Parse a message from the stream."""
        size = header.get_msg_size()
        cls = header.get_msg_cls()
        msg = self._parse_cls_from_stream(cls, size, stream)
        return msg

    def parse_packet(self, pkt_header, stream):
        """Parse a single packet."""
        count = pkt_header.NumberMsgs

        while count > 0:
            header = self._parse_cls_from_stream(MsgHeader, MsgHeader.header_size, stream)

            if header.is_known():
                msg = self.parse_msg(header, stream)
                yield msg
            else:
                offset = header.get_msg_size()
                stream.seek(offset, os.SEEK_CUR)

            count -= 1

    def parse_stream(self, stream):
        """Parse opened file-like stream."""
        while True:
            pkt_header = self._parse_cls_from_stream(
                PacketHeader,
                PacketHeader.header_size,
                stream,
            )

            msgs = self.parse_packet(pkt_header, stream)
            for msg in msgs:
                yield (pkt_header, msg)

    def parse_file(self, file_name):
        """Parse channel file."""
        with open(file_name, 'rb') as channel_file:
            for ret in self.parse_stream(channel_file):
                yield ret

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
        t = pkt_header.get_datetime()
        print t, msg

if __name__ == '__main__':
    main()
