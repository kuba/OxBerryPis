"""XDP stream headers."""
import struct
import datetime
from collections import namedtuple

from oxberrypis.parsing.fields import fields

from oxberrypis.parsing.utils import get_pkt_namedtuple
from oxberrypis.parsing.utils import get_pkt_format_string


# Packet Header
pkt_header_spec = (
    fields.PktSize,
    fields.DeliveryFlag,
    fields.NumberMsgs,
    fields.SeqNum,
    fields.SendTime,
    fields.SendTimeNS,
)

class PacketHeader(get_pkt_namedtuple('PacketHeader', pkt_header_spec)):
    """XDP feed packet header."""

    fmt = get_pkt_format_string(pkt_header_spec)
    header_size = struct.calcsize(fmt)

    def get_datetime(self):
        """Get datetime when the packet was sent to the multicast
        channel for publication."""
        timestamp = self.SendTime + self.SendTimeNS / 1000000000.0
        return datetime.datetime.utcfromtimestamp(timestamp)


# Message Header
msg_header_spec = (
    fields.MsgSize,
    fields.MsgType,
)

class MsgHeader(get_pkt_namedtuple('MsgHeader', msg_header_spec)):
    """XDP Message header."""
    fmt = get_pkt_format_string(msg_header_spec)
    header_size = struct.calcsize(fmt)

    """Mapping between known message types and known message classes."""
    known_msgs = {}

    @classmethod
    def register_known_msg(cls, msg_cls):
        """Decorator for registering known messages."""
        cls.known_msgs[msg_cls.msg_type] = msg_cls
        return msg_cls

    def is_known(self, known_msgs=None):
        """Checked whether payload message is known."""
        known_msgs = known_msgs or self.known_msgs
        return self.MsgType in known_msgs

    def get_msg_cls(self, known_msgs=None):
        """Get payload message class."""
        known_msgs = known_msgs or self.known_msgs
        return known_msgs.get(self.MsgType)

    def get_msg_size(self):
        """Return the size of the payload (message) only.

          Customers should not hard code msg sizes in feed handlers;
          instead the feed handler should use the Msg
          Size field to determine where the next message in the packet
          begins. This allows the XDP format to
          accommodate the different market needs for data content and
          allow the format to be more agile.

        """
        return self.MsgSize - self.header_size
