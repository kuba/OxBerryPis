"""Fields used in the XDP data stream packets."""
from oxberrypis.errors import OxBerryPisException

fields = {
    # Packet
    'PktSize': 2,
    'DeliveryFlag': 1,
    'NumberMsgs': 1,
    'SeqNum': 4,
    'SendTime': 4,
    'SendTimeNS': 4,

    # Messages
    'MsgSize': 2,
    'MsgType': 2,
    'SourceTimeNS': 4,
    'SymbolIndex': 4,
    'SymbolSeqNum': 4,
    'OrderID': 4,
    'Price': 4,
    'Volume': 4,
    'Side': 1,
    'OrderIDGTCIndicator': 1,
    'TradeSession': 1,
    'ReasonCode': 1,
    'TradeID': 4,

    # Message 220
    'SourceTime': 4,
    'TradeCond1': 1,
    'TradeCond2': 1,
    'TradeCond3': 1,
    'TradeCond4': 1,
    'TradeThroughExempt': 1,
    'LiquidityIndicatorFlag': 1,
    'AskPrice': 4,
    'AskVolume': 4,
    'BidPrice': 4,
    'BidVolume': 4,
}

size_mapping = {
    1: 'B',
    2: 'H',
    4: 'I',
}

class FieldsGenerator(object):
    """Fields generator for NYSE Arca Integrated Feed stream."""

    def __init__(self, fields, size_mapping):
        self.fields = fields
        self.size_mapping = size_mapping

    def __getattr__(self, field_name):
        if field_name not in self.fields:
            raise AttributeError("Field not found")

        field_format_size = self.fields[field_name]
        if field_format_size not in self.size_mapping:
            raise OxBerryPisException("Field has no size mapped")

        field_format = self.size_mapping[field_format_size]

        return (field_name, field_format)

fields = FieldsGenerator(fields, size_mapping)
