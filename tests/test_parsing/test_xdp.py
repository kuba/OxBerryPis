import unittest
import datetime

from oxberrypis.errors import OxBerryPisException


class TestGetPktFormatString(unittest.TestCase):

    def go(self, pkt_spec):
        from oxberrypis.parsing.xdp import get_pkt_format_string
        return get_pkt_format_string(pkt_spec)

    def test_empty(self):
        pkt_spec = ()
        self.assertTrue(self.go(pkt_spec), '<')

    def test_normal(self):
        pkt_spec = ((None, 'a'), (None, 'bc'))
        self.assertEqual(self.go(pkt_spec), '<abc')

    def test_non_string(self):
        pkt_spec = ((None, None),)
        with self.assertRaises(OxBerryPisException):
            self.go(pkt_spec)


class TestGetPktNamedtuple(unittest.TestCase):

    def go(self, name, pkt_spec):
        from oxberrypis.parsing.xdp import get_pkt_namedtuple
        return get_pkt_namedtuple(name, pkt_spec)

    def test_normal(self):
        name = 'Test'
        pkt_spec = (('abcd', None), ('xyz', None))
        ntuple = self.go(name, pkt_spec)
        self.assertEqual(('abcd', 'xyz'), ntuple._fields)

    def test_empty_fields(self):
        name = 'asd'
        ntuple = self.go(name, ())
        self.assertEqual(len(ntuple._fields), 0)

    def test_empty_name(self):
        name = ''
        with self.assertRaises(OxBerryPisException):
            ntuple = self.go(name, ())


class TestPacketHeader(unittest.TestCase):

    def setUp(self):
        from oxberrypis.parsing.xdp import PacketHeader
        self.cls = PacketHeader

    def test_get_datetime(self):
        send_time = 1324271989
        send_time_ns = 267963000
        model_dt = datetime.datetime(2011, 12, 19, 6, 19, 49, 267963)

        pkt_header = self.cls(0, 0, 0, 0, send_time, send_time_ns)
        pkt_dt = pkt_header.get_datetime()

        self.assertEqual(pkt_dt, model_dt)


class TestMessageHeader(unittest.TestCase):

    def setUp(self):
        from oxberrypis.parsing.xdp import MsgHeader
        self.cls = MsgHeader

    def test_is_known(self):
        for known_msg in self.cls.known_msgs:
            msg_hdr = self.cls(0, known_msg)
            self.assertTrue(msg_hdr.is_known())

    def test_is_not_know(self):
        msg_hdr = self.cls(0, None)
        self.assertFalse(msg_hdr.is_known())

    def test_get_msg_cls(self):
        for (known_msg, msg_cls) in self.cls.known_msgs.items():
            msg_hdr = self.cls(0, known_msg)
            self.assertEqual(msg_hdr.get_msg_cls(), msg_cls)
