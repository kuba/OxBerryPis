"""Order implementation.

Created on Apr 28, 2013

.. codeauthor:: Hynek Jemelik

"""


def enum(*sequential, **named):
    """Create enum type with (optionally) auto increment key."""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class Order(object):
    """An order in the order book."""

    types = enum('BUY', 'SELL')
    BUY = types.BUY
    SELL = types.SELL

    def __init__(self, order_id, limit_price, num_shares, order_type):
        self.id = order_id
        self.price = limit_price
        self.num_shares = num_shares
        self.type = order_type

    def key(self):
        if self.type == self.SELL:
            return self.price
        else:
            return -self.price
