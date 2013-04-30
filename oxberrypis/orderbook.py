"""Order book implementation."""

from oxberrypis.errors import OxBerryPisException


class Order(object):
    """Represents a single order."""

    def __init__(self, order_id, shares, limit, next_elem, prev_elem):
        self.order_id = order_id
        self.shares = shares
        self.limit = limit
        self.next_elem = next_elem
        self.prev_elem = prev_elem

    def remove(self):
        """Remove the order from the list."""
        if self.prev_elem is None and self.next_elem is None:
            # We are the last element so remove the limit as well.
            # Uncomment the follwing if we don't remove the limit (for
            # some reason)
            #self.limit.head_order = None
            #self.limit.tail_order = None
            self.limit.remove()
        elif self.prev_elem is None:
            # just remove us (we must be at the head of the queue)
            self.limit.head_order = self.next_elem
            self.next_elem.prev_elem = None
        elif self.next_elem is None:
            # we are at the tail
            self.limit.tail_order = self.prev_elem
            self.prev_elem.next_elem = None
        else:
            # we are in the morderIddle so
            self.prev_elem.next_elem = self.prev_elem
            self.next_elem.prev_elem = self.next_elem

class Limit(object):
    """Represents a limit price."""

    def __init__(self, price, book, head_order,
            tail_order, next_elem, prev_elem):
        self.price = price
        self.head_order = head_order
        self.tail_order = tail_order
        self.next_elem = next_elem
        self.prev_elem = prev_elem
        self.book = book

    def remove(self):
        """Remove ourselves.

        Note that we are in a stack with a dummy header.

        """
        self.prev_elem.next_elem = self.next_elem
        if self.next_elem is not None:
            self.next_elem.prev_elem = self.prev_elem

        # find ourselves in the map and remove
        if self.price in self.book.sell_limits:
            del self.book.sell_limits[self.price]
        elif self.price in self.book.buy_limits:
            del self.book.buy_limits[self.price]

    def add(self, order_id, price, amount):
        """Add an order at the tail."""
        x = self.tail_order
        o = Order(order_id, amount, self, None, x)
        if x is None:
            self.head_order = o
        else:
            x.next_elem = o
        self.tail_order = o

        return o

class LimitBook(object):
    """Represents a book of limits for a single share price."""

    def __init__(self):
        self.buy_limits = {}
        self.sell_limits = {}
        self.buy_orders = {}
        self.sell_orders = {}
        self.buy_front = Limit(0, None, None, None, None, None) # dummy headers
        self.sell_front = Limit(0, None, None, None, None, None)

    def add_buy(self, price, amount, order_id):
        """Add a sell order."""
        self.add_order(
            self.buy_limits,
            self.buy_front,
            self.buy_orders,
            price,
            amount,
            order_id,
        )

    def add_sell(self, price, amount, order_id):
        """Add a buy order."""
        self.add_order(
            self.sell_limits,
            self.sell_front,
            self.sell_orders,
            price,
            amount,
            order_id,
        )

    def modify_order(self, order_id, new_quantity):
        """Modify quantity of an order.

        Modifies an order of any type as the messages can't
        tell which type it is).

        """
        if order_id in self.buy_orders:
            self.buy_orders[order_id].shares = new_quantity

        elif order_id in self.buy_orders:
            self.sell_orders[order_id].shares = new_quantity
        else:
            raise OxBerryPisException('No Such Order: {}'.format(order_id))

    def get_sell_head_order(self):
        """Gets first sell order."""
        limit = self.sell_front.next_elem
        if limit is None:
            raise OxBerryPisExecption('No Sell Orders')
        else:
            return limit.head_order

    def get_buy_head_order(self):
        """Gets first buy order."""
        limit = self.buy_front.next_elem
        if limit is None:
            raise OxBerryPisExecption('No Buy Orders')
        else:
            return limit.head_order

    def remove_order(self, order_id):
        """Remove an order.

        Removes an order of any type as the messages can't
        tell which type it is).

        """
        if order_id in self.buy_orders:
            self.buy_orders[order_id].remove()
            del self.buy_orders[order_id]
        elif order_id in self.buy_orders:
            self.sell_orders[order_id].remove()
            del self.sell_orders[order_id]
        else:
            raise OxBerryPisException('No Such Order: {}'.format(order_id))

    def add_order(self, limits, front, orders, price, amount, order_id):
        """Add an order (paramterised by specifics)."""
        if price in limits:
            # if the limit exists get it from the map
            limit = limits[price]
        else:
            # otherwise find a postion and create a new limit
            a = self.search_list_from(front, price)
            limit = Limit(price, self, None, None, a.next_elem, a)
            a.next_elem = limit
            if limit.next_elem is not None:
                limit.next_elem.prev_elem = limit

        o = limit.add(order_id, price, amount)
        orders[order_id] = o

    def search_list_from(self, x, price):
        """Simple search."""
        while x.next_elem is not None and x.next_elem.price < price:
            x = x.next_elem

        return x
