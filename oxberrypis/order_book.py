'''
Created on Apr 28, 2013

@author: hynek
'''

from errors import OxBerryPisException
import fibonacci_heap
from linked_list import LinkedList

class OrderBook:
    def __init__(self):
        self.orders = {}
        self.limitbooks = {}
        self.book = fibonacci_heap.make_heap()
    
    def get_best(self):
        if fibonacci_heap.is_empty(self.book):
            return None
        else:
            limitbook_node = fibonacci_heap.minimum(self.book)
            limitbook = limitbook_node.data
            if limitbook.is_empty():
                # Removing empty limitbook'
                fibonacci_heap.extract(self.book)
                del self.limitbooks[abs(limitbook_node.key)]
                return self.get_best()
            else:
                return limitbook.get_first_value()
    
    def add_order(self, order):
        if order.id in self.orders:
            msg = 'Order {} already exists.'.format(order.id)
            raise OxBerryPisException(msg)
        if order.price not in self.limitbooks:
            limitbook = LinkedList()
            limitbook_node = fibonacci_heap.make_node(order.key(), limitbook)
            fibonacci_heap.insert(self.book, limitbook_node)
            self.limitbooks[order.price] = limitbook_node
        else:
            limitbook = self.limitbooks[order.price].data
        order_node = limitbook.append_value(order)
        self.orders[order.id] = order_node
    
    def remove_order(self, order_id):
        if order_id not in self.orders:
            return
        order_node = self.orders[order_id]
        price = order_node.data.price
        limitbook = self.limitbooks[price].data
        limitbook.remove_node(order_node)
        # We might at this point remove limitbook if it is empty,
        # but it might be better for performance reasons to keep it there.
        del self.orders[order_id]
    
    def update_order(self, updated_order):
        if updated_order.id not in self.orders:
            msg = 'Cannot update non-existing order {}.'.format(updated_order.id)
            raise OxBerryPisException(msg)
        order_node = self.orders[updated_order.id]
        order = order_node.data
        if updated_order.price == order.price:
            # We can do change locally inside limitbook
            if updated_order.num_shares < order.num_shares:
                # Order stays at its position in queue
                order_node.data = updated_order
            else:
                # Order moves at the end of queue
                limitbook = self.limitbooks[order.price].data
                limitbook.remove_node(order_node)
                updated_order_node = limitbook.append_value(updated_order)
                self.orders[updated_order.id] = updated_order_node
        else:
            # Changing price is equivalent to removing and adding again
            self.remove_order(order.id)
            self.add_order(updated_order)
        
            