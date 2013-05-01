import unittest

import io
import struct
import shutil
import os.path
import tempfile
from collections import namedtuple

from oxberrypis.errors import ParsingError


class DummyPkt(namedtuple('Dummy', 'a b')):
    fmt = 'II'

    @classmethod
    def get_dummy(cls):
        return DummyPkt(1, 2)

    @classmethod
    def pack_dummy(cls):
        return struct.pack(cls.fmt, 1, 2)

class DummyMsgHeader(object):
    fmt = 'I'
    header_size = struct.calcsize(fmt)

    def __init__(self, msg_cls, known=True, msg_size=0):
        self.known = known
        self.msg_cls = msg_cls
        self.msg_size = msg_size

    def is_known(self):
        return self.known

    def get_msg_cls(self):
        return self.msg_cls

    def get_msg_size(self):
        return self.msg_size

class DummyPacketHeader(namedtuple('DummyPacketHeader', 'no_msgs')):
    fmt = 'I'
    header_size = struct.calcsize(fmt)
    dummy_values = (1,)

    def __init__(self, msgs_num):
        self.NumberMsgs = msgs_num

    @classmethod
    def get_dummy(cls):
        return DummyPacketHeader(*cls.dummy_values)

    @classmethod
    def pack_dummy(cls):
        return struct.pack(cls.fmt, *cls.dummy_values)


class TestXDPChannelUnpacker(unittest.TestCase):

    def create_unpacker(self, stream=None):
        from oxberrypis.parsing.parser import XDPChannelUnpacker
        stream = stream or io.BytesIO()
        return (stream, XDPChannelUnpacker(stream))

    def setUp(self):
        self.stream, self.cu = self.create_unpacker()

    def packed_to_stream(self, *packed):
        for packed_item in packed:
            self.stream.write(packed_item)
        self.stream.seek(0)

    def test_parse_cls_from_stream(self):
        packed = DummyPacketHeader.pack_dummy()
        self.packed_to_stream(packed)
        parsed = self.cu.parse_cls_from_stream(
            DummyPacketHeader,
            DummyPacketHeader.header_size,
        )
        self.assertTrue(isinstance(parsed, DummyPacketHeader))
        model = DummyPacketHeader.get_dummy()
        self.assertEqual(parsed, model)

    def test_parse_cls_from_empty_stream(self):
        pkt = self.cu.parse_cls_from_stream(None, 0)
        self.assertTrue(pkt is None)

    def _test_parse_msg(self, payload=0):
        msg_size = struct.calcsize(DummyPkt.fmt)
        header = DummyMsgHeader(DummyPkt, msg_size=msg_size + payload)
        packed = DummyPkt.pack_dummy()
        self.packed_to_stream(packed)
        msg = self.cu.parse_msg(header)
        model = DummyPkt.get_dummy()
        self.assertTrue(isinstance(msg, DummyPkt))
        self.assertEqual(msg, model)

    def test_parse_msg(self):
        self._test_parse_msg()

    def test_parse_msg_bigger_payload(self):
        self._test_parse_msg(100)

    def test_parse_packet(self):
        return
        hdr = DummyPacketHeader(2)
        #msg1 = DummyMsgHeader(DummyPkt,
        stream = self.packed_to_stream(
            packed_msg_hdr1,
            packed_msg1,
            packed_msg_hdr2,
            packed_msg2,
        )
        self.cu.parse_packet(hdr, stream)

    def test_parse_stream(self):
        pass


class TestFileXDPChannelUnpacker(unittest.TestCase):

    def setUp(self):
        from oxberrypis.parsing.parser import FileXDPChannelUnpacker
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
