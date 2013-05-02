import unittest

from oxberrypis.errors import OxBerryPisException

from oxberrypis.orderbook import Order
from oxberrypis.orderbook import Limit
<<<<<<< HEAD
from oxberrypis.orderbook import LimitBook
from oxberrypis.errors import OxBerryPisException

class TestOrderBook(unittest.TestCase):
=======


class TestOrderBook(unittest.TestCase):

    def create_limit_book(self):
        from oxberrypis.orderbook import LimitBook
        return LimitBook()

>>>>>>> 8aa8087b3dc9b0b0fcb3f922130fde617e8e4a80
    def test_remove(self):
        lims = self.create_limit_book()
        lims.add_buy(10, 100, 1)
        self.assertEqual(lims.get_buy_head_order().order_id, 1)
        lims.remove_order(1)
<<<<<<< HEAD
        self.assertRaises(OxBerryPisException,lims.get_buy_head_order)
        lims = LimitBook()
        lims.add_sell(10,100,2)
        self.assertEqual(lims.get_sell_head_order().order_id,2)
        lims.remove_order(2)
        self.assertRaises(OxBerryPisException,lims.get_sell_head_order)

    def test_modify(self):
        lims = LimitBook()
        lims.add_buy(10,100,1)
        self.assertEqual(lims.get_buy_head_order().shares,100)
        lims.modify_order(1,110)
        self.assertEqual(lims.get_buy_head_order().shares,110)
        
        lims.add_sell(10,100,2)
        self.assertEqual(lims.get_sell_head_order().shares,100)
        lims.modify_order(2,110)
        self.assertEqual(lims.get_sell_head_order().shares,110)
=======
        self.assertRaises(OxBerryPisException, lims.get_buy_head_order)
        lims = self.create_limit_book()
        lims.add_sell(10, 100, 2)
        self.assertEqual(lims.get_sell_head_order().order_id, 2)
        lims.remove_order(1)
        self.assertRaises(OxBerryPisException, lims.get_sell_head_order)

    def test_modify(self):
        lims = self.create_limit_book()
        lims.add_buy(10, 100, 1)
        self.assertEqual(lims.get_buy_head_order().limit.price, 10)
        lims.modify_order(1, 11)
        self.assertEqual(lims.get_buy_head_order().limit.price, 11)

        lims.add_sell(10, 100, 2)
        self.assertEqual(lims.get_sell_head_order().limit.price, 10)
        lims.modify_order(2, 11)
        self.assertEqual(lims.get_sell_head_order().order.limit.price, 11)
>>>>>>> 8aa8087b3dc9b0b0fcb3f922130fde617e8e4a80

    def test_input(self):
        lims = self.create_limit_book()
        lims.add_buy(10, 100, 1)
        lims.add_buy(11, 100, 2)
        self.assertEqual(lims.get_buy_head_order().limit.price, 10)
        lims.add_buy(9, 100, 3)
        self.assertEqual(lims.get_buy_head_order().limit.price, 9)
        lims.add_buy(9, 100, 4)
        self.assertEqual(lims.get_buy_head_order().order_id, 3)
