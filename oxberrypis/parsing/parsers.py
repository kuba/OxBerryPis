"""Parsers for XDP streams."""
import os
import io
import struct
import os.path

from oxberrypis.errors import ParsingError

from oxberrypis.parsing.headers import PacketHeader
from oxberrypis.parsing.headers import MsgHeader


class XDPChannelUnpacker(object):
    """XDP channel parser (unpacker).

    The parser reads the supplied :py:attr:`stream`, unpacks packet
    headers, reads all message headers and unpacks only known messages.

    .. note::

       The parser assumes that the stream position is not manipulated
       during the lifetime of this object. Packets and messages are
       assumed to appear in the stream consecutively.

    The parsers uses :py:class:`.headers.PacketHeader` and
    :py:class:`.headers.MsgHeader` for parsing, but you can supply your
    own header classes by setting :py:attr:`pkt_hdr_cls` and
    :py:attr:`msg_header_cls` to appropriate values.

    :param stream: Readable stream which feeds the parser.
    :param pkt_hdr_cls: Packet header class. Defaults to
                        :py:class:`.headers.PacketHeader`.
    :param msg_hdr_cls: Message header class. Defaults to
                        :py:class:`.headers.MessageHeader`.

    """
    def __init__(self, stream, pkt_hdr_cls=None, msg_hdr_cls=None):
        if not stream.readable():
            raise ParsingError("The stream is not readable")

        self.stream = stream

        self.pkt_hdr_cls = pkt_hdr_cls or PacketHeader
        self.msg_hdr_cls = msg_hdr_cls or MsgHeader

    def parse_cls_from_stream(self, cls, size):
        """Read the stream and parse to create an instance of given class.

        Assumes ``cls._make`` is a method accepting a tuple of unpacked
        data.

        Returns ``None`` if the stream is empty and raises an error
        if unpacking failed.

        """
        data = self.stream.read(size)
        if not data:
            # stream is empty
            return None

        try:
            unpacked = struct.unpack_from(cls.fmt, data)
        except struct.error as e:
            raise ParsingError('Unpacking failed')

        parsed = cls._make(unpacked)
        return parsed

    def parse_msg(self, msg_header):
        """Parse a message from the stream.

        Message header is used to determined the size of the payload
        and the type of the message contained within it.

        """
        size = msg_header.get_msg_size()
        cls = msg_header.get_msg_cls()
        msg = self.parse_cls_from_stream(cls, size)
        return msg

    def advance(self, offset):
        """Skip ``offset`` number of bytes in the stream."""
        if self.stream.seekable():
            self.stream.seek(offset, os.SEEK_CUR)
        else:
            self.stream.read(offset)

    def parse_packet(self, pkt_header):
        """Generator for messages found within packet.

        Packet header is used to read off the number of messages
        contained within the packet. Then unpacks message headers one
        by one and if the message type is recognised, the message is
        parsed. Otherwise position of the stream is advanced.

        """
        count = pkt_header.NumberMsgs

        while count > 0:
            header = self.parse_cls_from_stream(
                self.msg_hdr_cls,
                self.msg_hdr_cls.header_size,
            )

            if header.is_known():
                msg = self.parse_msg(header)
                yield msg
            else:
                offset = header.get_msg_size()
                self.advance(offset)

            count -= 1

    def parse(self):
        """Generator for all the known messages from the stream.

        As long as there is a data remaining in the stream (assumed to
        be sufficiently long), it unpack the packet header. For each
        packet header parses the messages contained within.

        """
        while True:
            pkt_header = self.parse_cls_from_stream(
                self.pkt_hdr_cls,
                self.pkt_hdr_cls.header_size,
            )

            if pkt_header is None:
                # End reading the stream as no data remains
                break

            msgs = self.parse_packet(pkt_header)
            for msg in msgs:
                yield (pkt_header, msg)

        # Close the stream when we are done
        self.stream.close()


class FileXDPChannelUnpacker(XDPChannelUnpacker):
    """XDP channel parser (unpacker) with file stream."""

    """Standard channel file name."""
    CHANNEL_FILE_NAME_FMT = "20111219-ARCA_XDP_IBF_{}.dat"

    def __init__(self, channel_path, pkt_hdr_cls=None, msg_hdr_cls=None):
        """Initialise the parser with the stream from opened file."""
        stream = self.open_stream(channel_path)

        super(FileXDPChannelUnpacker, self).__init__(
            stream,
            pkt_hdr_cls,
            msg_hdr_cls,
        )

    def open_stream(self, channel_path):
        """Return opened stream for the given file found at ``channel_path``."""
        if not os.path.exists(channel_path):
            msg = "Channel {} not found".format(channel_path)
            raise ParsingError(msg)

        stream = io.open(channel_path, 'rb')

        return stream

    @classmethod
    def get_channel_path(cls, directory, channel, channel_file_name_fmt=None):
        """Get path to the channel found in the directory.

        Channel file name format string defaults to string set in
        :py:attr:`CHANNEL_FILE_NAME_FMT` but it may be changed by calling
        the function with appropriate ``channel_file_name_fmt`` value.

        """
        channel_file_name_fmt = channel_file_name_fmt or cls.CHANNEL_FILE_NAME_FMT
        file_name = channel_file_name_fmt.format(channel)
        path = os.path.join(directory, file_name)
        return path

    @classmethod
    def get_channel_unpacker(cls, directory, channel_id):
        """Factory for channel unpacker given ``directory`` and ``channel_id``."""
        channel_path = cls.get_channel_path(directory, channel_id)
        return cls(channel_path)
