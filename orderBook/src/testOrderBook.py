import unittest
import orderBook


class TestOrderBook(unittest.TestCase):

    def testExecute(self):
        # Set up an order book
        lims = orderBook.limitBook()
        lims.addBuy(10,200,1)
        lims.addSell(10,100,2)
        # test partial buy execution
        self.assertEqual( lims.execute() , (10,100))
        lims.addSell(11,100,3)
        # test no executo
        self.assertEqual(lims.execute() , (0,0))
        # test partial sell
        lims.addSell(10,200,4)
        self.assertEqual(lims.execute() , (10,100))
        
        # test equal
        lims.addBuy(10,100,5)
        
        self.assertEqual(lims.execute() , (10,100))
	
        lims.removeOrder(3)


if __name__ == '__main__':
    unittest.main()
