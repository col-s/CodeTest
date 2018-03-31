#!/usr/bin/python
# coding: utf8

import unittest
import datetime
import time
from collections import OrderedDict
import StockMarket


########################################################################
class StockMarketTest(unittest.TestCase):
    """"""

    #----------------------------------------------------------------------
    def setUp(self):
        """Create example stockmarket"""
        stocks = OrderedDict()
        stocks['TEA'] = StockMarket.Stock('TEA', 0, 100)
        stocks['POP'] = StockMarket.Stock('POP', 8, 100)
        stocks['ALE'] = StockMarket.Stock('ALE', 23, 60)
        GIN = StockMarket.StockPreferred('GIN', 8, 100, 2)
        JOE = StockMarket.Stock('JOE', 13, 250)
        self.market = StockMarket.StockMarket(stocks)
        self.market.addStock(GIN)
        self.market.addStock(JOE)

    def tearDown(self):
        self.market = None

    def test_dividend(self):
        price = 10
        results = [0, 0.8, 2.3, 0.2, 1.3]
        for stock, result in zip(self.market.stocks.values(), results):
            self.assertEqual(stock.calcDividend(price), result)

        self.assertEqual(self.market.stocks['JOE'].calcDividend(0), 'Invalid price, please try again')
        self.assertEqual(self.market.stocks['GIN'].calcDividend(-1), 'Invalid price, please try again')

    def test_calcPERatio(self):
        price = 10
        results = [0, 1.25, 0.43, 1.25, 0.77]
        for stock, result in zip(self.market.stocks.values(), results):
            self.assertEqual(stock.calcPERatio(price), result)

    def test_recordTrade(self):
        price = 10
        quantity = 100
        for stock in self.market.stocks.values():
            for indicator, option in zip(('bought', 'sold'), (True, False)):
                result = 'Timestamp:%s Number of Shares:%d %s at £%f' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                              quantity,
                                                                              indicator,
                                                                              price)
                self.assertEqual(stock.recordTrade(price, quantity, option), result)

    def test_calcVolWeightPrice(self):
        price = 10
        quantity = 100
        stock = self.market.stocks['TEA']
        for _ in range(10):
            stock.recordTrade(price, quantity)
            time.sleep(0.01)
        self.assertEqual(stock.calcVolWeightPrice(), 10)

    def test_allShareIndex(self):
        for stock in self.market.stocks.values():
            stock.price = 10
        self.assertEqual(self.market.allShareIndex, 10)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(StockMarketTest))
    return suite

def run():
    unittest.TextTestRunner().run(suite())

if __name__ == '__main__':
    run()