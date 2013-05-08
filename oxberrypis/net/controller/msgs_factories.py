"""Factories for stock messages.

These factories take messages from :py:module:`oxberrypis.parsing.messages`
and turn them into instances of :py:class:`.proto.stock_pb2.StockMessage`.

"""
from ..proto.stock_pb2 import StockMessage

from ...parsing.messages import OBAddOrderMsg
from ...parsing.messages import OBModifyMsg
from ...parsing.messages import OBDeleteMsg
from ...parsing.messages import OBExecutionMsg
from ...parsing.messages import TradeMsg


class StockMessageFactory(object):
    """Generic factory for stock message."""

    @classmethod
    def create_stock_msg(cls, msg):
        stock_msg = StockMessage()
        stock_msg.type = cls.msg_type

        field = getattr(stock_msg, cls.field_name)
        cls.process_field(msg, field)

        return stock_msg


class StockMessageAddFactory(StockMessageFactory):
    """Factory for add order stock message."""
    msg_type = StockMessage.ADD
    field_name = 'add'

    @classmethod
    def process_field(cls, msg, field):
        field.symbol_index = msg.SymbolIndex
        field.order_id = msg.OrderID
        field.price = msg.Price
        field.volume = msg.Volume
        field.side = msg.Side


class StockMessageModifyFactory(StockMessageFactory):
    """Factory for modify order stock message."""
    msg_type = StockMessage.MODIFY
    field_name = 'modify'

    @classmethod
    def process_field(cls, msg, field):
        field.symbol_index = msg.SymbolIndex
        field.order_id = msg.OrderID
        field.price = msg.Price
        field.volume = msg.Volume
        field.side = msg.Side


class StockMessageDeleteFactory(StockMessageFactory):
    """Factory for delete order stock message."""
    msg_type = StockMessage.DELETE
    field_name = 'delete'

    @classmethod
    def process_field(cls, msg, field):
        field.symbol_index = msg.SymbolIndex
        field.order_id = msg.OrderID
        field.side = msg.Side


class StockMessageExecutionFactory(StockMessageFactory):
    """Factory for execution order stock message."""
    msg_type = StockMessage.EXECUTE
    field_name = 'execution'

    @classmethod
    def process_field(cls, msg, field):
        field.symbol_index = msg.SymbolIndex
        field.order_id = msg.OrderID
        field.price = msg.Price
        field.volume = msg.Volume
        field.reason_code = msg.ReasonCode


class StockMessageTradeFactory(StockMessageFactory):
    """Factory for trade stock message."""
    msg_type = StockMessage.TRADE
    field_name = 'trade'

    @classmethod
    def process_field(cls, msg, field):
        field.symbol_index = msg.SymbolIndex


class StockMessagesFactory(object):
    """Factory for stock messages."""

    factories = {
        OBAddOrderMsg: StockMessageAddFactory,
        OBModifyMsg: StockMessageModifyFactory,
        OBDeleteMsg: StockMessageDeleteFactory,
        OBExecutionMsg: StockMessageExecutionFactory,
        TradeMsg: StockMessageTradeFactory,
    }

    @classmethod
    def create(cls, pkt_hdr, msg):
        msg_cls = msg.__class__
        if msg_cls not in cls.factories:
            return None

        factory = cls.factories[msg_cls]
        stock_msg = factory.create_stock_msg(msg)
        stock_msg.packet_time = pkt_hdr.SendTime
        stock_msg.packet_time_ns = pkt_hdr.SendTimeNS

        return stock_msg
