from backtrader import Strategy, indicators
EMA = indicators.ExponentialMovingAverage

class TestStrategy(Strategy):
    params = (
        ('maperiod', 15),
        ('printlog', False),
        ('ma', { 'name': 'ema', 'func': EMA })
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
        self.ma_slow = self.params.ma['func'](self.datas[0], period=self.params.maperiod)
        self.ma_fast = self.params.ma['func'](self.datas[0], period=round(self.params.maperiod/6))

    # Order placed event
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price, order.executed.value, order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price, order.executed.value, order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected' + str(order.status))

        self.order = None

    # Trade completed event
    def notify_trade(self, trade):
        if not trade.isclosed: return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    # On each data event
    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.datas[0].close[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            self.log('Pending Order...')
            return

        if self.ma_slow[0] < self.datas[0].close[0]:
            self.log('BUY SIGNAL, %.2f' % self.datas[0].close[0])
            self.order = self.buy()
        elif self.ma_slow[0] > self.datas[0].close[0]:
            self.log('SELL SIGNAL, %.2f' % self.datas[0].close[0])
            self.order = self.sell()

        if not self.position and self.ma_fast[0] < self.datas[0].close[0]:
            self.log('CATCH THE KNIFE!!!, %.2f' % self.datas[0].close[0])
            self.order = self.buy()

    def stop(self):
        self.log('({} Period {}) Ending Value {}'.format(self.params.ma['name'],
            self.params.maperiod, round(self.broker.getvalue())), doprint=True)

