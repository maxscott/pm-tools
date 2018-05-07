from __future__ import (absolute_import, division, print_function, unicode_literals)
from datetime import datetime  # For datetime objects
import os.path
import sys
import math
import argparse
import backtrader as bt
from backtrader import indicators as btind
from tam_strategy import TestStrategy

SMA = btind.SimpleMovingAverage
WMA = btind.WeightedMovingAverage
EMA = btind.ExponentialMovingAverage

MODPATH = os.path.dirname('/users/max/projects/fi/data/tam/')
T = True
F = False

class LongOnly(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        # buy max purchase tomorrow if possible
        if isbuy:
            try:
                return math.floor(cash/data.open[1])
            except:
                return 0
        # sell total position
        else:
            return self.broker.getposition(data).size

# assumes data at `modpath/{name}.csv`
def load_data(name, fromdate, todate):
    datapath = os.path.join(MODPATH, name + '.csv')
    return bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=fromdate,
        todate=todate,
        reverse=False)

def parse_arguments():
    parser=argparse.ArgumentParser(description='')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--optimize', nargs='+', help='')
    parser.add_argument('--backtest', type=int)
    return parser.parse_args()

def main():
    args = parse_arguments()
    v = args.verbose

    fromdate = datetime(2013, 1, 1)
    todate = datetime(2018, 3, 1)

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    ma_map = { 'sma': SMA, 'wma': WMA, 'ema': EMA }

    # Add a strategy
    if args.optimize:
        ma_min, ma_max = [int(a) for a in args.optimize]
        marange = range(ma_min, ma_max)
        matypes = [ {'name':k,'func':v} for k,v in ma_map.items() ]
        strats = cerebro.optstrategy(
            TestStrategy,
            ma=matypes,
            maperiod=marange,
            printlog=v)
    elif args.backtest:
        period = args.backtest
        strats = cerebro.addstrategy(TestStrategy, maperiod=period, printlog=v)
    else:
        raise ValueError('Pass either backtest or optimize options')


    for d in ['SPY']:
        cerebro.adddata(load_data(d, fromdate, todate))

    cerebro.broker.setcash(1000.0)
    cerebro.addsizer(LongOnly)
    cerebro.broker.setcommission(commission=0.0)

    cerebro.run()

    if args.backtest:
        cerebro.plot()

if __name__ == '__main__':
    main()
