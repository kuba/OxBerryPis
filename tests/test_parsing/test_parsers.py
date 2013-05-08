import unittest

import io
import struct
import shutil
import os.path
import tempfile
from collections import namedtuple

from oxberrypis.errors import ParsingError


class DummyMessage1(namedtuple('DummyMessage1', 'a b')):
    fmt = 'II'
    dummy = (1, 7,)

    @classmethod
    def get_dummy(cls):
        return cls(*cls.dummy)

    @classmethod
    def get_size(cls):
        return struct.calcsize(cls.fmt)

    def pack(self):
        return struct.pack(self.fmt, *self)

    @classmethod
    def get_header(cls):
        return DummyMsgHeader(cls.get_size(), 1)


class DummyMessage2(namedtuple('DummyMessage2', 'c')):
    fmt = 'c'
    dummy = ('!',)

    @classmethod
    def get_size(cls):
        return struct.calcsize(cls.fmt)

    @classmethod
    def get_dummy(cls):
        return cls(*cls.dummy)

    def pack(self):
        return struct.pack(self.fmt, *self)

    @classmethod
    def get_header(cls):
        return DummyMsgHeader(cls.get_size(), 2)


class DummyMsgHeader(namedtuple('DummyMsgHeader', 'size type')):
    fmt = 'II'
    header_size = struct.calcsize(fmt)

    known_msgs = {
        1: DummyMessage1,
        2: DummyMessage2,
    }

    def is_known(self):
        return self.type in self.known_msgs.keys()

    def get_msg_cls(self):
        assert self.is_known()
        return self.known_msgs[self.type]

    def get_msg_size(self):
        return self.size

    def pack(self):
        packed = struct.pack(self.fmt, *self)
        return packed


class DummyPacketHeader(namedtuple('DummyPacketHeader', 'NumberMsgs')):
    fmt = 'I'
    header_size = struct.calcsize(fmt)

    def pack(self):
        packed = struct.pack(self.fmt, *self)
        return packed


class UnreadableStrem(object):
    def readable(self):
        return False


class SeekableStream(object):
    def __init__(self, is_seekable):
        self.is_seekable = is_seekable
        self.position = 0

    def readable(self):
        return True

    def seekable(self):
        return self.is_seekable

    def seek(self, num, relative):
        assert self.is_seekable
        self.position += num

    def read(self, num):
        self.position += num


class TestXDPChannelUnpacker(unittest.TestCase):

    def get_cls(self):
        from oxberrypis.parsing.parsers import XDPChannelUnpacker
        return XDPChannelUnpacker

    def create_unpacker(self, stream=None):
        stream = stream or io.BytesIO()
        unpacker = self.cls(stream, DummyPacketHeader, DummyMsgHeader)
        return (stream, unpacker)

    def setUp(self):
        self.cls = self.get_cls()
        self.stream, self.cu = self.create_unpacker()

    def packed_to_stream(self, *packed):
        for packed_item in packed:
            self.stream.write(packed_item)
        self.stream.seek(0)

    def test_stream_not_readable(self):
        stream = UnreadableStrem()
        with self.assertRaises(ParsingError):
            self.cls(stream)

    def test_parse_cls_from_stream(self):
        model = DummyPacketHeader(69)
        packed = model.pack()
        self.packed_to_stream(packed)

        parsed = self.cu.parse_cls_from_stream(
            DummyPacketHeader,
            DummyPacketHeader.header_size,
        )

        self.assertTrue(isinstance(parsed, DummyPacketHeader))
        self.assertEqual(parsed, model)

    def test_parse_cls_from_empty_stream(self):
        pkt = self.cu.parse_cls_from_stream(None, 0)
        self.assertTrue(pkt is None)

    def test_unpacking_failed(self):
        self.stream.write('a')
        self.stream.seek(0)
        with self.assertRaises(ParsingError):
            self.cu.parse_cls_from_stream(
                DummyPacketHeader,
                DummyPacketHeader.header_size,
            )

    def _test_parse_msg(self, payload=0):
        msg_size = DummyMessage1.get_size()
        size = msg_size + payload
        header = DummyMsgHeader(size, 1)
        model = DummyMessage1.get_dummy()
        packed = model.pack()
        self.packed_to_stream(packed)
        msg = self.cu.parse_msg(header)
        self.assertTrue(isinstance(msg, DummyMessage1))
        self.assertEqual(msg, model)

    def test_parse_msg(self):
        self._test_parse_msg()

    def test_parse_msg_bigger_payload(self):
        self._test_parse_msg(100)

    def test_advance_seekable(self):
        stream = SeekableStream(True)
        parser = self.cls(stream)
        parser.advance(5)
        self.assertEqual(stream.position, 5)

    def test_advance_nonseekable(self):
        stream = SeekableStream(False)
        parser = self.cls(stream)
        parser.advance(5)
        self.assertEqual(stream.position, 5)

    def test_parse_packet(self):
        hdr = DummyPacketHeader(3)

        msg1 = DummyMessage1.get_dummy()
        packed_msg1 = msg1.pack()
        msg1_hdr = msg1.get_header()
        packed_msg1_hdr = msg1_hdr.pack()

        msg2_hdr = DummyMsgHeader(10, 3)
        packed_msg2_hdr = msg2_hdr.pack()
        packed_msg2 = ' ' * 10

        msg3 = DummyMessage2.get_dummy()
        packed_msg3 = msg3.pack()
        msg3_hdr = msg3.get_header()
        packed_msg3_hdr = msg3_hdr.pack()

        self.packed_to_stream(
            packed_msg1_hdr,
            packed_msg1,
            packed_msg2_hdr,
            packed_msg2,
            packed_msg3_hdr,
            packed_msg3,
        )

        parsed = self.cu.parse_packet(hdr)
        msgs = list(parsed)

        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0], msg1)
        self.assertEqual(msgs[1], msg3)

    def test_parse_empty_stream(self):
        parsed = list(self.cu.parse())
        count = len(parsed)
        self.assertEqual(count, 0)

    def packet_to_stream(self, *packets):
        packed = map(lambda p: p.pack(), packets)
        self.packed_to_stream(*packed)

    def test_parse(self):
        pkt_hdr1 = DummyPacketHeader(1)
        pkt_hdr2 = DummyPacketHeader(0)
        pkt_hdr3 = DummyPacketHeader(2)

        msg1 = DummyMessage1(34, 87)
        msg2 = DummyMessage2('@')
        msg3 = DummyMessage1(100, 4235)

        msg1_hdr = msg1.get_header()
        msg2_hdr = msg2.get_header()
        msg3_hdr = msg3.get_header()

        self.packet_to_stream(
            pkt_hdr1,
            msg1_hdr,
            msg1,
            pkt_hdr2,
            pkt_hdr3,
            msg2_hdr,
            msg2,
            msg3_hdr,
            msg3,
        )

        parsed = list(self.cu.parse())
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0], (pkt_hdr1, msg1))
        self.assertEqual(parsed[1], (pkt_hdr3, msg2))
        self.assertEqual(parsed[2], (pkt_hdr3, msg3))


class TestFileXDPChannelUnpacker(unittest.TestCase):

    def setUp(self):
        from oxberrypis.parsing.parsers import FileXDPChannelUnpacker
        self.cls = FileXDPChannelUnpacker

    def test_get_channel_path(self):
        channel_path = self.cls.get_channel_path('asd', 1, 'ABC{}XYZ')
        model_path = os.path.join('asd', 'ABC1XYZ')
        self.assertEqual(channel_path, model_path)

    def test_get_channel_path_default(self):
        channel_path = self.cls.get_channel_path('asd', 1)
        model_fmt = self.cls.CHANNEL_FILE_NAME_FMT.format(1)
        model_path = os.path.join('asd', model_fmt)
        self.assertEqual(channel_path, model_path)

    def create_stream_source_file(self):
        directory = tempfile.mkdtemp()
        channel_id = 0
        path = self.cls.get_channel_path(directory, channel_id)
        open(path, 'wb').close()
        return (directory, channel_id, path)

    def test_open_stream(self):
        _, _, path = self.create_stream_source_file()
        unpacker = self.cls(path)
        self.assertEqual(unpacker.stream.name, path)

    def test_channel_not_found(self):
        directory = tempfile.mkdtemp()
        path = os.path.join(directory, 'channel0')
        with self.assertRaises(ParsingError):
            self.cls(path)

    def test_get_channel_unpacker(self):
        directory, channel_id, _ = self.create_stream_source_file()
        self.cls.get_channel_unpacker(directory, channel_id)
        shutil.rmtree(directory)
