#!/usr/bin/python
# coding: utf8

import unittest
import datetime
import time
from collections import OrderedDict
import StockMarket


########################################################################
class StockMarketTest(unittest.TestCase):
    """Unit tests for StockMarket"""

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
        self.market.add_stock(GIN)
        self.market.add_stock(JOE)
        self.invalid_price = 'Invalid price, must be greater' \
            ' than 0.0, please try again.'

    def tearDown(self):
        self.market = None

    def test_dividend(self):
        test_values = {2: (0, 4, 11.5, 1, 6.5),
                      10: (0, 0.8, 2.3, 0.2, 1.3),
                      150: (0, 0.05, 0.15, 0.01, 0.09)}
        for price, results in test_values.items():
            for stock, result in zip(self.market.stocks.values(), results):
                self.assertEqual(stock.calc_dividend(price), result)

        self.assertEqual(self.market.stocks['JOE'].calc_dividend(0),
                         self.invalid_price)
        self.assertEqual(self.market.stocks['GIN'].calc_dividend(-1),
                         self.invalid_price)

    def test_calc_PE_ratio(self):
        test_values = {10: (0, 1.25, 0.43, 1.25, 0.77),
                      150: (0, 18.75, 6.52, 18.75, 11.54),
                      5000: (0, 625.0, 217.39, 625.0, 384.62)}
        for price, results in test_values.items():
            for stock, result in zip(self.market.stocks.values(), results):
                self.assertEqual(stock.calc_PE_ratio(price), result)

        self.assertEqual(self.market.stocks['JOE'].calc_PE_ratio(0),
                         self.invalid_price)

    def test_precision(self):
        price = 10
        test_values = {0: (0, 1, 0, 1, 1),
                      1: (0, 1.3, 0.4, 1.3, 0.8),
                      5: (0, 1.25, 0.43478, 1.25, 0.76923)}
        for precision, results in test_values.items():
            for stock, result in zip(self.market.stocks.values(), results):
                stock.precision = precision
                self.assertEqual(stock.calc_PE_ratio(price), result)

    def test_record_trade(self):
        price = 10
        quantity = 100
        for stock in self.market.stocks.values():
            for indicator, option in zip(('bought', 'sold'), (True, False)):
                result = 'Timestamp:{0} Number of Shares: {1} {2} at £{3}'.format(
                    datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    quantity,
                    indicator,
                    price)
                self.assertEqual(stock.record_trade(price, quantity, option),
                                 result)

    def test_calc_vol_weight_price(self):
        test_values = {10: ((10, 100), (10, 100), (10, 100),
                            (10, 100), (10, 100),
                           (10, 100), (10, 100), (10, 100),
                           (10, 100), (10, 100)),
                      7.73: ((8, 150), (11, 89), (15, 10), (7, 300), (4, 50))}
        stocks = (self.market.stocks['TEA'], self.market.stocks['POP'])
        for stock, (result, values) in zip(stocks, test_values.items()):
            for price, quantity in values:
                stock.record_trade(price, quantity)
                time.sleep(0.01)
            self.assertEqual(stock.calc_vol_weight_price(), result)

    def test_all_share_index(self):
        test_values = {10: (10, 10, 10, 10, 10),
                      8.01:(15, 5, 7, 3, 21),
                      245.95: (100, 150, 500, 1000, 120)}
        for index, prices in test_values.items():
            for stock, price in zip(self.market.stocks.values(), prices):
                stock.price = price
            self.assertEqual(self.market.all_share_index, index)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(StockMarketTest))
    return suite

def run():
    unittest.TextTestRunner().run(suite())

if __name__ == '__main__':
    run()
