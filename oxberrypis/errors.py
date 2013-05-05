"""Exceptions."""

class OxBerryPisException(Exception):
    """Base class for errors in the oxberrypis package."""

class OrderBookError(OxBerryPisException):
    """Order book related error."""
