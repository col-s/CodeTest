#!/usr/bin/python
# coding: utf8

import datetime
from collections import OrderedDict, namedtuple

Trade = namedtuple('Trade',['price','quantity'])

########################################################################
class StockMarket(object):
    """Stock market object"""

    #----------------------------------------------------------------------
    def __init__(self, stocks=OrderedDict()):
        """
        Args:
            stocks = OrderedDict() of namedtuple
        """
        self._stocks = stocks
        self._precision = 2


    @property
    def stocks(self):
        return self._stocks

    @property
    def allShareIndex(self):
        """returns GBCE All Share Index
        Calculates the geometric mean by multiplying all the stock prices in the market
        and returns the nth root where n = number of stocks
        """
        if len(self._stocks) == 0: return 0.0
        totalSharePrices = 1
        for k, v in self.stocks.iteritems():
            totalSharePrices *= v.price
        return round(totalSharePrices**(1.0/len(self.stocks)), self._precision)

    @property
    def precision(self):
        """Precision of decimal place"""
        return self._precision

    @precision.setter
    def precision(self, val):
        """Sets the precision"""
        if val >= 0:
            self._precision = val
        else:
            self._precision = 0
            print 'Minimum precision amount is 0.'

    def addStock(self, stock):
        """adds a stock object to the stock list"""
        self._stocks[stock.name] = stock


########################################################################
class Stock(object):
    """Common Stock"""

    #----------------------------------------------------------------------
    def __init__(self, name, lastDividend, parValue, price=0):
        """
        Args:
            name = string
            lastDividen = int
            parValue = int
            price = int share price in pennies
        """
        self._name = name
        self._lastDividend = lastDividend
        self._parValue = parValue
        self._price = price
        self._trades = {}
        self._precision = 2
        self._invalidPriceWarning = 'Invalid price, must be greater than 0.0, please try again.'

    @property
    def name(self):
        """Name of the stock"""
        return self._name

    @property
    def price(self):
        """Price of the stock"""
        return self._price

    @price.setter
    def price(self, val):
        """Sets the stock price"""
        if val > 0:
            self._price = val
        else:
            raise ValueError(self._invalidPriceWarning)

    @property
    def lastDividend(self):
        """Last dividend of stock"""
        return self._lastDividend

    @lastDividend.setter
    def lastDividend(self, val):
        """Set last dividend of stock"""
        self._lastDividend = val

    @property
    def precision(self):
        """Precision of decimal place"""
        return self._precision

    @precision.setter
    def precision(self, val):
        """Sets the precision"""
        if val >= 0:
            self._precision = val
        else:
            self._precision = 0
            print 'Minimum precision amount is 0.'

    def calcDividend(self, price):
        """calculates the dividend based on the stock type"""
        if price > 0:
            return round(float(self.lastDividend) / price, self._precision)
        else:
            return self._invalidPriceWarning

    def calcPERatio(self, price):
        """calculates the PE Ratio"""
        if price > 0:
            try:
                return round(price / float(self.lastDividend), self._precision)
            except ZeroDivisionError:
                # where the last dividend was zero we return a value of zero
                return 0
        else:
            return self._invalidPriceWarning

    def calcVolWeightPrice(self, time=15):
        """
        calculates the volume weighted stock price
        sum ((price * quantity) of each trade) / sum(quantity of each trade)
        for the total transactions in the given time peroid (minutes)
        """
        trades = self._getLatestTransactions(time)
        if len(trades) == 0:
            print 'No trades recorded to calculate price in last %d minutes' % time
        totalCost = 0
        totalQuantity = 0
        for trade in trades:
            totalCost += trade.price * trade.quantity
            totalQuantity += trade.quantity
        return round(float(totalCost) / totalQuantity, self._precision)

    def recordTrade(self, price, quantity, buy=True, currency='£'):
        """
        records a trade with timestamp, quantity of shares,
        buy or sell indicator and traded price. Currency defaults to GBP
        Stores each transaction in a dictionary with timestamp as key
        and tuple of share price and number of shares traded
        """
        if price <= 0:
            return self._invalidPriceWarning
        if quantity <= 0:
            return 'Invalid quantity, must be greater than 0, please try again.'
        
        timeStamp = datetime.datetime.now()
        self._trades[timeStamp] = Trade(price, quantity)
        indicator = 'bought' if buy else 'sold'
        return 'Timestamp:%s Number of Shares:%d %s at %s%f' % (timeStamp.strftime('%Y-%m-%d %H:%M:%S'),
                                                                self._trades[timeStamp].quantity,
                                                                indicator,
                                                                currency,
                                                                self._trades[timeStamp].price)

    def _getLatestTransactions(self, time=15):
        """
        returns list the latest n transactions in the specified
        time period (minutes)
        Returns: list of tuples (price, quantity) where
                            price = in of trading price
                            quantity = int no of shares traded
        """
        currentTime = datetime.datetime.now()
        startTime = currentTime - datetime.timedelta(minutes=time)
        validTransactions = []
        for timeStamp, transactionData in reversed(self._trades.items()):
            if timeStamp > startTime:
                validTransactions.append(transactionData)
            else: break
        return validTransactions


########################################################################
class StockPreferred(Stock):
    """Preferred option stock, inherits from common Stock class"""

    #----------------------------------------------------------------------
    def __init__(self, name, lastDividend, parValue, fixedDividend, price=0):
        """
        Args:
            name = string
            lastDividen = int
            parValue = int
            price = int share price in pennies
            fixedDividend = int (percentage)
        """
        super(StockPreferred, self).__init__(name, lastDividend, parValue, price)
        self._fixedDividend = fixedDividend

    def calcDividend(self, price):
        """calculates the dividend based on the stock type"""
        if price > 0:
            return round((float(self._fixedDividend * self._parValue) / 100) / price, self._precision)
        else:
            return self._invalidPriceWarning