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
    return bt.feeds.GenericCSVData(
        dataname=datapath,
        fromdate=fromdate,
        todate=todate,
        reverse=False,
        dtformat='%Y-%m-%d',
        close=5,
        open=5,
        volume=6,
        )

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid date")

def parse_arguments():
    parser=argparse.ArgumentParser(description='')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--start', type=valid_date, required=True)
    parser.add_argument('--end', type=valid_date, required=True)
    parser.add_argument('--ma', nargs='+', help='')
    parser.add_argument('--backtest', type=int)
    return parser.parse_args()

def main():
    args = parse_arguments()
    v = args.verbose
    fromdate, todate = args.start, args.end
    ma_map = { 'sma': SMA, 'wma': WMA, 'ema': EMA }

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    if args.ma:
        ma_min, ma_max = [int(a) for a in args.ma]
        marange = range(ma_min, ma_max)
        matypes = [ {'name':k,'func':v} for k,v in ma_map.items() ]
        strats = cerebro.optstrategy(
            TestStrategy, ma=matypes, maperiod=marange, mafast=range(50,75), printlog=v)
    elif args.backtest:
        period = args.backtest
        strats = cerebro.addstrategy(TestStrategy, maperiod=period, printlog=v)
    else:
        raise ValueError('Pass either backtest or ma options')


    for d in ['SPY']:
        cerebro.adddata(load_data(d, fromdate, todate))

    cerebro.broker.setcash(10000.0)
    cerebro.addsizer(LongOnly)
    cerebro.broker.setcommission(commission=0.00)

    cerebro.run()

    if args.backtest:
        cerebro.plot(iplot=True, style='line')

if __name__ == '__main__':
    main()
