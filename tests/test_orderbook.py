import unittest

from oxberrypis.orderbook import Order
from oxberrypis.orderbook import Limit
from oxberrypis.orderbook import LimitBook

class TestOrderBook(object):
    def test_remove(self):
        lims = LimitBook()
        lims.add_buy(10,100,1)
        self.assertEqual(lims.get_buy_head_order().order_id,1)
        lims.remove_order(1)
        self.assertRaises(OxBerryPisException,lims.get_buy_head_order)
        lims = LimitBook()
        lims.add_sell(10,100,2)
        self.assertEqual(lims.get_sell_head_order().order_id,2)
        lims.remove_order(1)
        self.assertRaises(OxBerryPisException,lims.get_sell_head_order)

    def test_modify(self):
        lims = LimitBook()
        lims.add_buy(10,100,1)
        self.assertEqual(lims.get_buy_head_order().limit.price,10)
        lims.modify_order(1,11)
        self.assertEqual(lims.get_buy_head_order().limit.price,11)
        
        lims.add_sell(10,100,2)
        self.assertEqual(lims.get_sell_head_order().limit.price,10)
        lims.modify_order(2,11)
        self.assertEqual(lims.get_sell_head_order().order.limit.price,11)

    def test_input(self):
        lims = LimitBook()
        lims.add_buy(10,100,1)
        lims.add_buy(11,100,2)
        self.assertEqual(lims.get_buy_head_order().limit.price,10)
        lims.add_buy(9,100,3)
        self.assertEqual(lims.get_buy_head_order().limit.price,9)
        lims.add_buy(9,100,4)
        self.assertEqual(lims.get_buy_head_order().order_id,3)
