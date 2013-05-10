"""Order book matching engine.

Created on Apr 28, 2013

.. codeauthor:: Hynek Jemelik

"""
from ..errors import OrderBookError

from .book import OrderBook
from .order import Order


class PrintingMatchingEngineCallback(object):
    def trade(self, num_shares, price):
        print 'Trading {} shares at price {}.'.format(num_shares, price)


class MatchingEngine(object):
    """Matching engine.

    Main class for processing each individual stock, it implements
    rules and logic of stock exchange and maintains orders in correct
    order. It allows adding, changing, and removing orders.

    """
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
    
    def decrease_order_amount_by(self, order_id, decr_by):
        o = self.supply.get_order_by_id(order_id)
        if o is not None:
            self.update_order(o.id, o.price, o.num_shares - decr_by, o.type)
        else:
            o = self.demand.get_order_by_id(order_id)
            if o is not None:
                self.update_order(o.id, o.price, o.num_shares - decr_by, o.type)
            else:
                msg = 'Order with id {} has not been found.'.format(order_id)
                raise OrderBookError(msg)
        
    
    def get_best_orders(self):
        return (self.supply.get_best(), self.demand.get_best())
    
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
            if o1.type == Order.SELL:
                sell = o1
                buy = o2
            else:
                buy = o1
                sell = o2
            return sell.price <= buy.price

    def get_book(self, order):
        if order.type == Order.SELL:
            return self.supply
        elif order.type == Order.BUY:
            return self.demand
        else:
            msg = 'Order type {} not recognized.'.format(order.type)
            raise OrderBookError(msg)

    def get_opposite(self, order):
        if order.type == Order.SELL:
            return self.demand
        elif order.type == Order.BUY:
            return self.supply
        else:
            msg = 'Order type {} not recognized.'.format(order.type)
            raise OrderBookError(msg)
