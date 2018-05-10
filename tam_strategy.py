from backtrader import Strategy, indicators
EMA = indicators.ExponentialMovingAverage

class TestStrategy(Strategy):
    params = (
        ('maperiod', 126),
        ('mafast', 64),
        ('printlog', False)
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # To keep track of pending orders and buy price/commission
        self.order = self.buyprice = self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.mas = []
        self.ma_fasts = []

        for i,d in enumerate(self.datas):
            self.mas.append(EMA(d, period=self.params.maperiod))
            self.ma_fasts.append(EMA(d, period=round(self.params.mafast)))

    # Order placed event
    def notify_order(self, order):
        # Buy/Sell order submitted/accepted to/by broker - Nothing to do
        if order.status in [order.Submitted, order.Accepted]:
            return

        # Check if an order has been completed: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price, order.executed.value, order.executed.comm), doprint=True)
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price, order.executed.value, order.executed.comm), doprint=True)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected' + str(order.status))

        self.order = None

    # On each data event
    def next(self):
        for i,d in enumerate(self.datas):
            close = d.close[0]
            ma, ma_fast = self.mas[i][0], self.ma_fasts[i][0]
            self.log('Close, {}'.format(close))

            if ma < ma_fast:
                self.log('BUY SIGNAL, %.2f' % close)
                self.order = self.buy(data=d)
            elif ma_fast < ma:
                self.log('SELL SIGNAL, %.2f' % close)
                self.order = self.sell(data=d)
            else:
                self.order = None

    # Trade completed event
    def notify_trade(self, trade):
        if not trade.isclosed: return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def stop(self):
        broker_val = round(self.broker.getvalue())
        self.log('(Period {}, Fast {}) Ending Value {}'.format(self.params.maperiod, self.params.mafast, broker_val), doprint=True)

