from __future__ import (absolute_import, division, print_function, unicode_literals)
import datetime  # For datetime objects
import os.path
import sys
import backtrader as bt
from tam_strategy import TestStrategy

modpath = os.path.dirname('/users/max/projects/fi/data/tam/')
datapath = os.path.join(modpath, 'SPY.csv')

def main():
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    strats = cerebro.optstrategy(TestStrategy, maperiod=range(5, 20))

    # Create a Data Feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2003, 1, 1),
        todate=datetime.datetime(2018, 3, 1),
        reverse=False)

    cerebro.adddata(data)
    cerebro.broker.setcash(1000.0)
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)
    cerebro.broker.setcommission(commission=0.0)

    cerebro.run()

if __name__ == '__main__':
    main()
