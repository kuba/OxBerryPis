"""Order book matching engine.

Created on Apr 28, 2013

.. codeauhtor:: Hynek Jemelik

"""
from ..errors import OxBerryPisException
from .book import OrderBook
from .order import Order

class PrintingMatchingEngineCallback(object):
    def trade(self, num_shares, price):
        print 'Trading {} shares at price {}.'.format(num_shares, price)


class MatchingEngine(object):
    def __init__(self, callback=None):
        self.supply = OrderBook()
        self.demand = OrderBook()
        self.callback = callback or PrintingMatchingEngineCallback()

    def add_order(self, order_id, limit_price, num_shares, order_type):
        order = Order(order_id, limit_price, num_shares, order_type)
        book = self.get_book(order)
        book.add_order(order)
        self.execute_orders(order)

    def remove_order(self, order_id):
        self.supply.remove_order(order_id)
        self.demand.remove_order(order_id)

    def update_order(self, order_id, limit_price, num_shares, order_type):
        updated_order = Order(order_id, limit_price, num_shares, order_type)
        book = self.get_book(updated_order)
        book.update_order(updated_order)
        self.execute_orders(updated_order)

    def execute_orders(self, order):
        opposite = self.get_opposite(order)
        best = opposite.get_best()
        if self.can_trade(order, best):
            num_shares = min(order.num_shares, best.num_shares)
            self.callback.trade(num_shares, best.price)
            order.num_shares -= num_shares
            best.num_shares -= num_shares
            if best.num_shares == 0:
                self.remove_order(best.id)
            if order.num_shares == 0:
                self.remove_order(order.id)
            else:
                self.execute_orders(order)

    def can_trade(self, o1, o2):
        if o1 is None or o2 is None:
            return False
        else:
            if o1.type == "sell":
                sell = o1
                buy = o2
            else:
                buy = o1
                sell = o2
            return sell.price <= buy.price

    def get_book(self, order):
        if order.type == "sell":
            return self.supply
        elif order.type == "buy":
            return self.demand
        else:
            msg = 'Order type {} not recognized.'.format(order.type)
            raise OxBerryPisException(msg)

    def get_opposite(self, order):
        if order.type == "sell":
            return self.demand
        elif order.type == "buy":
            return self.supply
        else:
            msg = 'Order type {} not recognized.'.format(order.type)
            raise OxBerryPisException(msg)
