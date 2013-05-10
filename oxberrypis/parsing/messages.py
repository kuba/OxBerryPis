"""NYSE integrated feed messages."""
from oxberrypis.parsing.fields import fields

from oxberrypis.parsing.headers import MsgHeader

from oxberrypis.parsing.utils import get_pkt_format_string
from oxberrypis.parsing.utils import get_pkt_namedtuple


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
