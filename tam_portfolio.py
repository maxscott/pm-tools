import math

class PortfolioManager:
    def __init__(self, asset_percentages, cash=10000):
        # reference to percentages and for `dict.fromkeys()`
        self._assets = asset_percentages.items()
        self.signal_level = dict.fromkeys(self._assets, 0)

        # start with each assets' positions at 0
        self.model_positions = {a:{'amt':0,'last':0} for (a,p) in self._assets}
        self.actual_positions = {a:{'amt':0,'last':0} for (a,p) in self._assets}

        # start with each assets' totals amount * percentages' cash
        self.model_cash = { a:p*cash for (a,p) in self._assets }
        self.actual_cash = { a:p*cash for (a,p) in self._assets }

    def update_price(self, asset, price):
        self.model_positions[asset]['last'] = price
        self.actual_positions[asset]['last'] = price

    def update_signal(self, asset, signal_level):
        self.signal_level[asset] = signal_level
        self._update_model_asset(asset)

    def _update_model_asset(self, asset):
        a_pos = self.actual_positions[asset]
        a_cash = self.actual_cash[asset]
        sig_level = self.signal_level[asset]

        a_allocated = a_pos['amt'] * a_pos['last'] + a_cash
        sig_amount = math.floor(a_allocated * sig_level / a_pos['last'])

        self.model_positions[asset]['amt'] = m_amt = sig_amount
        self.model_cash[asset] = a_allocated - (m_amt * a_pos['last'])

    def purchase_asset(self, asset, amt, price):
        self.update_price(asset, price)
        self.actual_positions[asset]['amt'] += amt
        self.actual_cash[asset] -= amt * price

    def sell_asset(self, asset, amt, price):
        self.update_price(asset, price)
        self.actual_positions[asset]['amt'] -= amt
        self.actual_cash[asset] += amt * price

    # positive indicates a need to *purchase* that value's worth of asset
    # negative indicates a need to *sell* that value's worth of asset
    def get_model_difference(self, asset):
        m_amt  = self.model_positions[asset]['amt']
        m_last = self.model_positions[asset]['last']
        a_amt  = self.actual_positions[asset]['amt']
        a_last = self.actual_positions[asset]['last']
        return m_amt * m_last - a_amt * a_last

    def get_all_differences(self):
        return {a:self.get_model_difference(a) for (a,d) in self._assets}

    def get_total_value(self):
        return sum([
            sum([v for (k,v) in self.actual_cash.items()]),
            sum([v['amt']*v['last'] for (k,v) in self.actual_positions.items()])
        ])

