"""NYSE XDP feed structure."""
import struct
from collections import namedtuple

import datetime

from oxberrypis.parsing.fields import fields
from oxberrypis.errors import OxBerryPisException


def get_pkt_format_string(pkt_spec):
    """Create struct format string from spec tuple."""
    format_string = '<' # little endian

    for (field_name, field_format) in pkt_spec:
        if not isinstance(field_format, basestring):
            raise OxBerryPisException("Field format is not a string")

        format_string += field_format

    return format_string

def get_pkt_namedtuple(name, pkt_spec):
    """Create namedtuple from spec tuple."""
    if len(name) == 0:
        raise OxBerryPisException("Packet must have a name")
    fields = ' '.join([field[0] for field in pkt_spec])
    return namedtuple(name, fields)


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


# Order Book Add Order Message
msg100_spec = (
    fields.SourceTimeNS,
    fields.SymbolIndex,
    fields.SymbolSeqNum,
    fields.OrderID,
    fields.Price,
    fields.Volume,
    fields.Side,
    fields.OrderIDGTCIndicator,
    fields.TradeSession,
)

@MsgHeader.register_known_msg
class OBAddOrderMsg(get_pkt_namedtuple('OBAddOrderMsg', msg100_spec)):
    """Order Book Add Order Message."""
    fmt = get_pkt_format_string(msg100_spec)
    msg_type = 100


# Order Book Modify Message
msg101_spec = (
    fields.SourceTimeNS,
    fields.SymbolIndex,
    fields.SymbolSeqNum,
    fields.OrderID,
    fields.Price,
    fields.Volume,
    fields.Side,
    fields.OrderIDGTCIndicator,
    fields.ReasonCode,
)

@MsgHeader.register_known_msg
class OBModifyMsg(get_pkt_namedtuple('OBModifyMsg', msg101_spec)):
    """Order Book Modify Message."""
    fmt = get_pkt_format_string(msg101_spec)
    msg_type = 101


# Order Book Delete Message
msg102_spec = (
    fields.SourceTimeNS,
    fields.SymbolIndex,
    fields.SymbolSeqNum,
    fields.OrderID,
    fields.Side,
    fields.OrderIDGTCIndicator,
    fields.ReasonCode,
)

@MsgHeader.register_known_msg
class OBDeleteMsg(get_pkt_namedtuple('OBDeleteMsg', msg102_spec)):
    """Order Book Delete Message."""
    fmt = get_pkt_format_string(msg102_spec)
    msg_type = 102


# Order Book Execution Message
msg103_spec = (
    fields.SourceTimeNS,
    fields.SymbolIndex,
    fields.SymbolSeqNum,
    fields.OrderID,
    fields.Price,
    fields.Volume,
    fields.OrderIDGTCIndicator,
    fields.ReasonCode,
    fields.TradeID,
)

@MsgHeader.register_known_msg
class OBExecutionMsg(get_pkt_namedtuple('OBExecutionMsg', msg103_spec)):
    """Order Book Execution Message."""
    fmt = get_pkt_format_string(msg103_spec)
    msg_type = 103


# Trade Message
msg220_spec = (
    fields.SourceTime,
    fields.SourceTimeNS,
    fields.SymbolIndex,
    fields.SymbolSeqNum,
    fields.TradeID,
    fields.Price,
    fields.Volume,
    fields.TradeCond1,
    fields.TradeCond2,
    fields.TradeCond3,
    fields.TradeCond4,
    fields.TradeThroughExempt,
    fields.LiquidityIndicatorFlag,
    fields.AskPrice,
    fields.AskVolume,
    fields.BidPrice,
    fields.BidVolume,
)

@MsgHeader.register_known_msg
class TradeMsg(get_pkt_namedtuple('TradeMsg', msg220_spec)):
    """Trade Message."""
    fmt = get_pkt_format_string(msg220_spec)
    msg_type = 220
