import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch, MagicMock
from app.utils.currency_tracker import CurrencyTracker, plot_currency_dynamics


class TestPlotCurrencyDynamics(unittest.TestCase):
    def test_returns_figure(self):
        fig = plot_currency_dynamics("USD", 7)
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, "axes"))

    def test_different_currency(self):
        fig = plot_currency_dynamics("EUR", 14)
        self.assertIsNotNone(fig)


class TestCurrencyTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = CurrencyTracker()

    def test_init(self):
        self.assertIn("cbr.ru", self.tracker.base_url)

    @patch("app.utils.currency_tracker.requests.get")
    def test_get_current_rates_success(self, mock_get):
        xml = (
            '<?xml version="1.0" encoding="windows-1251"?>'
            '<ValCurs Date="18.06.2026" name="Foreign Currency Market">'
            '<Valute>'
            '<NumCode>840</NumCode>'
            '<CharCode>USD</CharCode>'
            '<Nominal>1</Nominal>'
            '<Name>Доллар США</Name>'
            '<Value>90,1234</Value>'
            '</Valute>'
            '</ValCurs>'
        )
        mock_resp = MagicMock()
        mock_resp.content = xml.encode("windows-1251")
        mock_get.return_value = mock_resp

        df = self.tracker.get_current_rates()
        self.assertIsNotNone(df)
        self.assertIn("CharCode", df.columns)
        self.assertIn("Value", df.columns)

    @patch("app.utils.currency_tracker.requests.get")
    @patch("builtins.print")
    def test_get_current_rates_failure(self, mock_print, mock_get):
        mock_get.side_effect = Exception("Network error")
        result = self.tracker.get_current_rates()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
