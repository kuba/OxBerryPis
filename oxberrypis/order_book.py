'''
Created on Apr 28, 2013

@author: hynek
'''

from errors import OxBerryPisException

class OrderBook:
    """
        Keeps order in iether demand or supply for single stock.
    """
    def create_book_structure(self):
        from fibonacci_heap import FibonacciHeap
        return FibonacciHeap()
    
    def create_price_level_structure(self):
        from linked_list import LinkedList
        return LinkedList()
    
    def __init__(self):
        self.orders = {}
        self.pricelevels = {}
        self.book = self.create_book_structure()
    
    def get_best(self):
        if self.book.is_empty():
            return None
        else:
            pricelevel_node = self.book.minimum()
            pricelevel = pricelevel_node.data
            if pricelevel.is_empty():
                # Removing empty pricelevel'
                self.book.extract()
                del self.pricelevels[abs(pricelevel_node.key)]
                return self.get_best()
            else:
                return pricelevel.front()
    
    def add_order(self, order):
        if order.id in self.orders:
            msg = 'Order {} already exists.'.format(order.id)
            raise OxBerryPisException(msg)
        if order.price not in self.pricelevels:
            pricelevel = self.create_price_level_structure()
            pricelevel_node = self.book.insert(order.key(), pricelevel)
            self.pricelevels[order.price] = pricelevel_node
        else:
            pricelevel = self.pricelevels[order.price].data
        order_node = pricelevel.add(order)
        self.orders[order.id] = order_node
    
    def remove_order(self, order_id):
        if order_id not in self.orders:
            return
        order_node = self.orders[order_id]
        price = order_node.data.price
        pricelevel = self.pricelevels[price].data
        pricelevel.remove(order_node)
        # We might at this point remove pricelevel if it is empty,
        # but it might be better for performance reasons to keep it there.
        del self.orders[order_id]
    
    def update_order(self, updated_order):
        if updated_order.id not in self.orders:
            msg = 'Cannot update non-existing order {}.'.format(updated_order.id)
            raise OxBerryPisException(msg)
        order_node = self.orders[updated_order.id]
        order = order_node.data
        if updated_order.price == order.price:
            # We can do change locally inside pricelevel
            if updated_order.num_shares < order.num_shares:
                # Order stays at its position in queue
                order_node.data = updated_order
            else:
                # Order moves at the end of queue
                pricelevel = self.pricelevels[order.price].data
                pricelevel.remove(order_node)
                updated_order_node = pricelevel.add(updated_order)
                self.orders[updated_order.id] = updated_order_node
        else:
            # Changing price is equivalent to removing and adding again
            self.remove_order(order.id)
            self.add_order(updated_order)
        
            