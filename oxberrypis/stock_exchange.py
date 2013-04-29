'''
Created on Apr 28, 2013

@author: hynek
'''

from errors import OxBerryPisException
from order_book import OrderBook
from order import Order

class StockExchange:
    def __init__(self):
        self.supply = OrderBook()
        self.demand = OrderBook()
    
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
            print 'Trading {} shares at price {}.'.format(num_shares, best.price)
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
    
def test():
    s = StockExchange()
    s.add_order(1, 10, 7000, "buy")
    # 10: -7000
    s.add_order(2, 10, 1000, "sell")
    # Trading 1000 shares at price 10.
    # 10: -6000
    s.add_order(3, 12, 9000, "sell")
    # 12 +9000, 10: -6000
    s.add_order(4, 11, 1000, "sell")
    # 12 +9000, 11: +1000, 10: -6000
    s.update_order(3, 12, 6000, "sell")
    # 12: +6000, 11: +1000, 10: -6000
    s.add_order(5, 12, 8000, "buy")
    # Trading 1000 shares at price 11.
    # Trading 6000 shares at price 12.
    # 12: -1000, 10: -6000
    s.add_order(6, 12, 2000, "buy")
    # 12: -3000, 10: -6000
    s.add_order(7, 12, 3000, "buy")
    # 12: -6000, 10: -6000
    s.update_order(6, 12, 4000, "buy")
    # 12: -8000, 10: -6000
    s.add_order(8, 13, 6000, "sell")
    # 13: +6000, 12: -8000, 10: -6000
    s.add_order(9, 12, 7000, "sell")
    # Trading 1000 shares at price 12.
    # Trading 3000 shares at price 12.
    # Trading 3000 shares at price 12.
    # 13: +6000, 12: -1000, 10: -6000
    s.add_order(10, 11, 2000, "sell")
    # Trading 1000 shares at price 12.
    # 13: +6000, 11: +1000, 10: -6000
    s.add_order(11, 11, 3000, "buy")
    # Trading 1000 shares at price 11.
    # 13: +6000, 11: -2000, 10: -6000
    s.remove_order(11)
    # 13: +6000, 10: -6000
    s.add_order(12, 8, 3000, "sell")
    # Trading 3000 shares at price 10.
    # 13: +6000, 10: -3000
    
if __name__ == '__main__':
    test()
        