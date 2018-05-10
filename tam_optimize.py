from __future__ import (absolute_import, division, print_function, unicode_literals)
from datetime import datetime  # For datetime objects
import os.path
import sys
import math
import argparse
import backtrader as bt
from backtrader import indicators as btind
from tam_strategy import TestStrategy

EMA = btind.ExponentialMovingAverage

MODPATH = os.path.dirname('/users/max/projects/fi/data/tam/')
T = True
F = False

class LongOnly(bt.Sizer):
    def _getsizing(self, comminfo, cash, data, isbuy):
        # sell total position
        if not isbuy:
            return self.broker.getposition(data).size

        # buy max purchase tomorrow if possible
        try:
            return math.floor(cash/data.open[1])
        except:
            return math.floor(cash/data.open[0])

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

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    if args.ma:
        ma_min, ma_max = [int(a) for a in args.ma]
        marange = range(ma_min, ma_max)
        strats = cerebro.optstrategy(
            TestStrategy,
            maperiod=marange,
            mafast=64,
            printlog=v)
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
