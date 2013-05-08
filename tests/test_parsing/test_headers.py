import unittest
import datetime


class TestPacketHeader(unittest.TestCase):

    def setUp(self):
        from oxberrypis.parsing.headers import PacketHeader
        self.cls = PacketHeader

    def test_get_datetime(self):
        send_time = 1324271989
        send_time_ns = 267963000
        model_dt = datetime.datetime(2011, 12, 19, 5, 19, 49, 267963)

        pkt_header = self.cls(0, 0, 0, 0, send_time, send_time_ns)
        pkt_dt = pkt_header.get_datetime()

        self.assertEqual(pkt_dt, model_dt)


class TestMessageHeader(unittest.TestCase):

    def setUp(self):
        from oxberrypis.parsing.headers import MsgHeader
        self.cls = MsgHeader

    def test_is_known(self):
        known_msgs = { 1: None }
        msg_hdr = self.cls(0, 1)
        self.assertTrue(msg_hdr.is_known(known_msgs))

    def test_is_not_know(self):
        known_msgs = { 1: None }
        msg_hdr = self.cls(0, 2)
        self.assertFalse(msg_hdr.is_known(known_msgs))

    def test_get_msg_cls(self):
        cls = object()
        known_msgs = { 9: cls }
        msg_hdr = self.cls(0, 9)
        self.assertEqual(msg_hdr.get_msg_cls(known_msgs), cls)

    def test_get_msg_size(self):
        delta = 10
        msg_hdr = self.cls(self.cls.header_size + delta, 0)
        self.assertEqual(msg_hdr.get_msg_size(), delta)

