"""Offline regression checks for the findings in test-results/REPORT.md."""

import math
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

import pandas as pd
import streamlit as st
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from calculations import (
    calculate_portfolio_comparison,
    calculate_portfolio_returns,
    calculate_rolling_volatility,
    calculate_sector_allocation,
    calculate_stock_performance,
)
from data_loader import load_prices
from stock_info import get_stock_info


def sample_download(tickers, **kwargs):
    """Return deliberately reordered columns, including missing provider data."""
    symbols = [tickers] if isinstance(tickers, str) else tickers
    index = pd.bdate_range("2022-01-03", periods=90)
    prices = pd.DataFrame(index=index)
    for ticker in sorted(set(symbols)):
        slope = sum(map(ord, ticker)) % 9 / 10 + 0.1
        prices[ticker] = [100 + slope * i + 2 * math.sin(i) for i in range(len(index))]
        if ticker in {"ZZZZINVALID123", "NOPRICE"}:
            prices[ticker] = float("nan")
    return pd.concat({"Close": prices}, axis=1)


def sample_ticker(ticker):
    info = {"longName": f"{ticker} Company", "sector": "Technology"}
    if ticker == "ZZZZINVALID123":
        info = {"trailingPegRatio": None}
    return Mock(info=info)


class CalculationRegressions(unittest.TestCase):
    def setUp(self):
        # The source column order differs from the portfolio and weight order.
        self.prices = pd.DataFrame({"JNJ": [100, 90, 80], "MSFT": [100, 110, 130]})
        self.weights = pd.Series({"MSFT": 1.0, "JNJ": 0.0})

    def test_weighted_returns_and_comparison_follow_ticker_labels(self):
        returns = calculate_portfolio_returns(self.prices, self.weights)
        expected = self.prices["MSFT"].pct_change().dropna()
        pd.testing.assert_series_equal(returns, expected, check_names=False)
        comparison = calculate_portfolio_comparison(
            self.prices, self.weights, self.prices[["MSFT"]], pd.Series({"MSFT": 1.0})
        )
        self.assertAlmostEqual(comparison.loc[0, "Portfolio A"], 0.3)
        self.assertAlmostEqual(comparison.loc[0, "Portfolio B"], 0.3)
        volatility = calculate_rolling_volatility(self.prices, self.weights, window=2)
        self.assertAlmostEqual(volatility.iloc[-1], expected.std() * math.sqrt(252))

    def test_holdings_returns_and_weights_keep_ticker_labels(self):
        holdings = calculate_stock_performance(self.prices, ["MSFT", "JNJ"], self.weights)
        holdings = holdings.set_index("Ticker")
        self.assertAlmostEqual(holdings.loc["MSFT", "Total Return"], 0.3)
        self.assertAlmostEqual(holdings.loc["JNJ", "Total Return"], -0.2)
        self.assertEqual(holdings.loc["MSFT", "Weight"], 1)

    def test_sector_allocation_aligns_metadata_with_weights(self):
        stocks = [{"Ticker": "JNJ", "Sector": "Health"}, {"Ticker": "MSFT", "Sector": "Tech"}]
        self.assertEqual(calculate_sector_allocation(stocks, self.weights), {"Health": 0, "Tech": 1})

    def test_incomplete_weights_and_empty_returns_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "match"):
            calculate_portfolio_returns(self.prices, pd.Series({"MSFT": 1}))
        with self.assertRaisesRegex(ValueError, "Not enough"):
            calculate_portfolio_returns(self.prices.iloc[:1], self.weights)


class ProviderRegressions(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()

    @patch("data_loader.yf.download", side_effect=sample_download)
    def test_download_restores_requested_order_and_deduplicates(self, download):
        prices = load_prices(["MSFT", "JNJ", "MSFT"])
        self.assertEqual(list(prices.columns), ["MSFT", "JNJ"])

    @patch("data_loader.yf.download", side_effect=sample_download)
    def test_missing_symbol_is_not_silently_removed(self, download):
        with self.assertRaisesRegex(ValueError, "NOPRICE"):
            load_prices(["MSFT", "NOPRICE"])

    @patch("data_loader.yf.download")
    def test_empty_single_day_and_disjoint_data_are_rejected(self, download):
        for prices in [pd.DataFrame(), pd.DataFrame({"MSFT": [100]}),
                       pd.DataFrame({"MSFT": [100, 101, None, None],
                                     "JNJ": [None, None, 100, 101]})]:
            with self.subTest(prices=prices):
                st.cache_data.clear()
                download.return_value = pd.concat({"Close": prices}, axis=1)
                with self.assertRaises(ValueError):
                    load_prices(list(prices.columns) or ["MSFT"])

    @patch("stock_info.yf.Ticker")
    def test_metadata_requires_a_name_and_accepts_short_name(self, ticker):
        ticker.side_effect = [Mock(info={"trailingPegRatio": None}), Mock(info={"shortName": "ETF"})]
        info = get_stock_info(["BAD", "FUND"])
        self.assertEqual(info[0]["Company"], "Invalid Ticker")
        self.assertEqual(info[1]["Company"], "ETF")


class DashboardRegressions(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()
        download = patch("data_loader.yf.download", side_effect=sample_download)
        metadata = patch("stock_info.yf.Ticker", side_effect=sample_ticker)
        download.start()
        metadata.start()
        self.addCleanup(download.stop)
        self.addCleanup(metadata.stop)
        self.app = AppTest.from_file(str(ROOT / "src/dashboard.py"), default_timeout=20).run()
        self.assertFalse(self.app.exception)

    def add_stock(self, ticker):
        self.app.text_input(key="new_ticker").set_value(ticker)
        next(button for button in self.app.button if button.label == "Add").click().run()
        self.assertFalse(self.app.exception)

    def test_add_callback_clears_input_and_rejects_invalid_or_duplicate(self):
        self.add_stock(" googl ")
        self.assertIn("GOOGL", self.app.session_state.portfolio)
        self.assertEqual(self.app.text_input(key="new_ticker").value, "")
        for ticker in [" aapl ", "ZZZZINVALID123", "NOPRICE"]:
            self.add_stock(ticker)
            self.assertTrue(self.app.error)
            self.assertEqual(len(self.app.session_state.portfolio), 7)

    def test_remove_last_holding_and_recover_by_adding(self):
        for ticker in self.app.session_state.portfolio.copy():
            self.app.button(key=f"remove_{ticker}").click().run()
            self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state.portfolio, [])
        self.assertEqual(len(self.app.metric), 0)
        self.add_stock("MSFT")
        self.assertEqual(self.app.session_state.portfolio, ["MSFT"])
        self.assertTrue(self.app.metric)

    def test_comparison_rejects_partial_data_and_recovers(self):
        for value in ["ZZZZINVALID123", "AAPL, NOPRICE"]:
            next(field for field in self.app.text_input
                 if field.label == "Enter Portfolio B tickers").set_value(value).run()
            self.assertFalse(self.app.exception)
            self.assertTrue(self.app.error)
            self.assertEqual(len(self.app.dataframe), 1)
        next(field for field in self.app.text_input
             if field.label == "Enter Portfolio B tickers").set_value(" aapl, AAPL ").run()
        self.assertFalse(self.app.exception)
        self.assertFalse(self.app.error)
        self.assertEqual(len(self.app.dataframe), 2)
        actual = self.app.dataframe[1].value.loc[0, "Portfolio B"]
        prices = sample_download(["AAPL"])["Close"]["AAPL"]
        self.assertAlmostEqual(actual, prices.iloc[-1] / prices.iloc[0] - 1)


if __name__ == "__main__":
    unittest.main()
