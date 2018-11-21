#!/usr/bin/python
# coding: utf8

import datetime
from collections import OrderedDict, namedtuple

Trade = namedtuple('Trade', ['price', 'quantity'])


class StockMarket(object):
    """Stock market object"""

    def __init__(self, stocks=None):
        """
        Args:
            stocks = OrderedDict() of namedtuple
        """
        self._stocks = stocks or OrderedDict()
        self._precision = 2

    @property
    def stocks(self):
        return self._stocks

    @property
    def all_share_index(self):
        """returns GBCE All Share Index
        Calculates the geometric mean by multiplying
        all the stock prices in the market
        and returns the nth root where n = number of stocks
        """
        if len(self._stocks) == 0:
            return 0.0
        total_share_prices = 1
        for k, v in self.stocks.iteritems():
            total_share_prices *= v.price
        return round(total_share_prices**(1.0/len(self.stocks)), self._precision)

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

    def add_stock(self, stock):
        """adds a stock object to the stock list"""
        self._stocks[stock.name] = stock


class Stock(object):
    """Common Stock"""

    def __init__(self, name, last_dividend, par_value, price=0):
        """
        Args:
            name = string
            last_dividend = int
            par_value = int
            price = int share price in pennies
        """
        self._name = name
        self._last_dividend = last_dividend
        self._par_value = par_value
        self._price = price
        self._trades = {}
        self._precision = 2
        self._invalid_price_warning = 'Invalid price, must be greater' \
            ' than 0.0, please try again.'

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
            raise ValueError(self._invalid_price_warning)

    @property
    def last_dividend(self):
        """Last dividend of stock"""
        return self._last_dividend

    @last_dividend.setter
    def last_dividend(self, val):
        """Set last dividend of stock"""
        self._last_dividend = val

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

    def calc_dividend(self, price):
        """calculates the dividend based on the stock type"""
        if price > 0:
            return round(float(self.last_dividend) / price, self._precision)
        else:
            return self._invalid_price_warning

    def calc_pe_ratio(self, price):
        """calculates the PE Ratio"""
        if price > 0:
            try:
                return round(price / float(self.last_dividend),
                             self._precision)
            except ZeroDivisionError:
                # where the last dividend was zero we return a value of zero
                return 0
        else:
            return self._invalid_price_warning

    def calc_vol_weight_price(self, time=15):
        """
        calculates the volume weighted stock price
        sum ((price * quantity) of each trade) / sum (quantity of each trade)
        for the total transactions in the given time period (minutes)
        """
        trades = self._get_latest_transactions(time)
        if len(trades) == 0:
            print 'No trades recorded to calculate price' \
                  ' in last {} minutes'.format(time)
        total_cost = 0
        total_quantity = 0
        for trade in trades:
            total_cost += trade.price * trade.quantity
            total_quantity += trade.quantity
        return round(float(total_cost) / total_quantity, self._precision)

    def record_trade(self, price, quantity, buy=True, currency='£'):
        """
        records a trade with timestamp, quantity of shares,
        buy or sell indicator and traded price. Currency defaults to GBP
        Stores each transaction in a dictionary with timestamp as key
        and tuple of share price and number of shares traded
        """
        if price <= 0:
            return self._invalid_price_warning
        if quantity <= 0:
            return 'Invalid quantity, must be greater than 0,' \
                   ' please try again.'

        time_stamp = datetime.datetime.now()
        self._trades[time_stamp] = Trade(price, quantity)
        indicator = 'bought' if buy else 'sold'
        return 'Timestamp:{0} Number of Shares: {1} {2} at {3}{4}'.format(
            time_stamp.strftime('%Y-%m-%d %H:%M:%S'),
            self._trades[time_stamp].quantity,
            indicator,
            currency,
            self._trades[time_stamp].price)

    def _get_latest_transactions(self, time=15):
        """
        returns list of the latest n transactions in the specified
        time period (minutes)
        Returns: list of tuples (price, quantity) where
                            price = int of trading price
                            quantity = int no of shares traded
        """
        current_time = datetime.datetime.now()
        start_time = current_time - datetime.timedelta(minutes=time)
        valid_transactions = []
        for time_stamp, transactionData in reversed(self._trades.items()):
            if time_stamp > start_time:
                valid_transactions.append(transactionData)
            else:
                break
        return valid_transactions


class StockPreferred(Stock):
    """Preferred option stock, inherits from common Stock class"""

    def __init__(self, name, last_dividend,
                 par_value, fixed_dividend, price=0):
        """
        Args:
            name = string
            last_dividen = int
            par_value = int
            price = int share price in pennies
            fixed_dividend = int (percentage)
        """
        super(StockPreferred, self).__init__(name, last_dividend,
                                             par_value, price)
        self._fixed_dividend = fixed_dividend

    def calc_dividend(self, price):
        """calculates the dividend based on the stock type"""
        if price > 0:
            return round((float(self._fixed_dividend * self._par_value)
                          / 100) / price, self._precision)
        else:
            return self._invalid_price_warning
