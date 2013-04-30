import unittest

import os.path
import struct
from collections import namedtuple
import StringIO
import tempfile

from oxberrypis.errors import OxBerryPisException


class DummyPkt(namedtuple('Dummy', 'a b')):
    fmt = 'II'
    size = struct.calcsize(fmt)

    @classmethod
    def get_dummy(cls):
        return DummyPkt(1, 2)

    @classmethod
    def pack_dummy(cls):
        return struct.pack(cls.fmt, 1, 2)

class DummyMsgHeader(object):
    fmt = 'I'
    size = struct.calcsize(fmt)

    def __init__(self, msg_cls, known=True):
        self.known = known
        self.msg_cls = msg_cls

    def is_known(self):
        return self.known

    def get_msg_cls(self):
        return self.msg_cls

class DummyPacketHeader(object):
    fmt = 'I'
    size = struct.calcsize(fmt)

    def __init__(self, msgs_num):
        self.NumberMsgs = msgs_num


class TestChannelParser(unittest.TestCase):

    def create_parser(self):
        from oxberrypis.parsing.parser import ChannelParser
        return ChannelParser()

    def setUp(self):
        self.cp = self.create_parser()

    def test__get_channel_path(self):
        channel_path = self.cp._get_channel_path('ABC{}XYZ', 'asd', 1)
        model_path = os.path.join('asd', 'ABC1XYZ')
        self.assertEqual(channel_path, model_path)

    def packed_to_stream(self, *packed):
        stream = StringIO.StringIO()
        for packed_item in packed:
            stream.write(packed_item)
        stream.seek(0)
        return stream

    def test_parse_cls_from_stream(self):
        packed = DummyPkt.pack_dummy()
        stream = self.packed_to_stream(packed)
        parsed = self.cp._parse_cls_from_stream(DummyPkt, stream)
        self.assertTrue(isinstance(parsed, DummyPkt))
        model = DummyPkt.get_dummy()
        self.assertEqual(parsed, model)

    def test_parse_msg(self):
        header = DummyMsgHeader(DummyPkt)
        packed = DummyPkt.pack_dummy()
        stream = self.packed_to_stream(packed)
        msg = self.cp.parse_msg(header, stream)
        model = DummyPkt.get_dummy()
        self.assertTrue(isinstance(msg, DummyPkt))
        self.assertEqual(msg, model)

    def tes_parse_packet(self):
        hdr = DummyPacketHeader(2)
        #msg1 = DummyMsgHeader(DummyPkt,
        stream = self.packed_to_stream(
            packed_msg_hdr1,
            packed_msg1,
            packed_msg_hdr2,
            packed_msg2,
        )
        self.cp.parse_packet(hdr, stream)

    def test_parse_stream(self):
        pass

    def test_parse_channel_not_found(self):
        tmp_directory_path = tempfile.mkdtemp()
        channel_id = 0

        with self.assertRaises(OxBerryPisException):
            self.cp.parse_channel(tmp_directory_path, channel_id)

    def test_parse_channel(self):
        tmp_directory_path = tempfile.mkdtemp()
        channel_id = 0

        channel_path = self.cp.get_channel_path(tmp_directory_path, channel_id)
        # Touch file
        open(channel_path, 'w').close()

        self.cp.parse_channel(tmp_directory_path, channel_id)
