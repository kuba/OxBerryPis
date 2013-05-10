"""Various utilities used in the parsing module."""
from collections import namedtuple

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
