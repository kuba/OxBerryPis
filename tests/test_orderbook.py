import unittest



from oxberrypis.stock_exchange import StockExchange 

from oxberrypis.errors import OxBerryPisException

class TestOrderBook(unittest.TestCase):
    def test_remove(self):
        lims = StockExchange()
        lims.add_order(1,10,100,"buy")
        self.assertEqual(lims.get_buy_head_order().id,1)
        lims.remove_order(1)
        self.assertIs(None,lims.get_buy_head_order())
        lims.add_order(2,10,100,"sell")
        self.assertEqual(lims.get_sell_head_order().id,2)
        lims.remove_order(2)
        self.assertIs(None,lims.get_sell_head_order())

    def test_modify(self):
        lims = StockExchange()
        lims.add_order(1,10,100,"buy")
        self.assertEqual(lims.get_buy_head_order().num_shares,100)
        self.assertEqual(lims.get_buy_head_order().price,10)
        lims.update_order(1,11,110,"buy")
        self.assertEqual(lims.get_buy_head_order().num_shares,110)
        self.assertEqual(lims.get_buy_head_order().price,11)

        lims.add_order(2,10,100,"sell")
        self.assertEqual(lims.get_sell_head_order().num_shares,100)
        self.assertEqual(lims.get_sell_head_order().price,10)
        lims.update_order(2,11,110,"sell")
        self.assertEqual(lims.get_sell_head_order().num_shares,110)
        self.assertEqual(lims.get_sell_head_order().price,11)

    def test_input(self):
        lims = StockExchange()
        lims.add_order(1,10,100,"buy")
        lims.add_order(2,10,100,"buy")
        self.assertEqual(lims.get_buy_head_order().id,1)
        lims.add_order(3,11,100,"buy")
        self.assertEqual(lims.get_buy_head_order().id,3)
        lims.add_order(4,9,100,"buy")
        self.assertEqual(lims.get_buy_head_order().id,3)
        
