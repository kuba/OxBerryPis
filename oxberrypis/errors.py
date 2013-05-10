"""Exceptions."""


class OxBerryPisException(Exception):
    """Base class for errors in the oxberrypis package."""


class ParsingError(OxBerryPisException):
    """General parsing error."""


class OrderBookError(OxBerryPisException):
    """Order book related error."""
