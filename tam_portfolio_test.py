import unittest
from tam_portfolio import PortfolioManager

class TestPortfolioManager(unittest.TestCase):
    def setUp(self):
        self.p = PortfolioManager({'spy': .6, 'bnd': .4}, cash=10000)

    def test_instantiation(self):
        self.assertEqual(self.p.model_positions['spy']['amt'], 0)
        self.assertEqual(self.p.model_positions['spy']['last'], 0)
        self.assertEqual(self.p.actual_positions['spy']['amt'], 0)
        self.assertEqual(self.p.actual_positions['spy']['last'], 0)
        self.assertEqual(self.p.model_cash['spy'], 6000)
        self.assertEqual(self.p.actual_cash['spy'], 6000)
        self.assertEqual(self.p.get_total_value(), 10000)

    def test_update_price(self):
        self.p.update_price('spy', 150)

        self.assertEqual(self.p.model_positions['spy']['last'], 150)
        self.assertEqual(self.p.actual_positions['spy']['last'], 150)

    def test_update_signal(self):
        self.p.update_price('spy', 150)
        self.p.update_signal('spy', 0)
        self.assertEqual(self.p.model_positions['spy']['amt'], 0)
        self.assertEqual(self.p.model_cash['spy'], 6000)
        self.p.update_signal('spy', .5)
        self.assertEqual(self.p.model_positions['spy']['amt'], 6000/150*.5)
        self.assertEqual(self.p.model_cash['spy'], 3000)
        self.p.update_signal('spy', 1)
        self.assertEqual(self.p.model_positions['spy']['amt'], 6000/150)
        self.assertEqual(self.p.model_cash['spy'], 0)

    def test_purchase_asset_price(self):
        self.p.purchase_asset('spy', amt=1, price=151)

        self.assertEqual(self.p.actual_positions['spy']['amt'], 1)
        self.assertEqual(self.p.actual_positions['spy']['last'], 151)
        self.assertEqual(self.p.actual_cash['spy'], 6000-151)

    def test_sell_asset_price(self):
        self.p.sell_asset('spy', amt=1, price=151)

        self.assertEqual(self.p.actual_positions['spy']['amt'], -1)
        self.assertEqual(self.p.actual_positions['spy']['last'], 151)
        self.assertEqual(self.p.actual_cash['spy'], 6151)

    def test_get_model_actual_value_differences(self):
        self.p.purchase_asset('spy', amt=10, price=150)
        self.p.update_price('bnd', 19)

        self.p.update_signal('spy', 1)
        self.assertEqual(self.p.get_all_differences(),{'spy': 4500,'bnd':0})
        self.p.update_signal('bnd', 1)
        self.assertEqual(self.p.get_all_differences(),{'spy': 4500,'bnd':3990})

if __name__ == '__main__':
    unittest.main()
