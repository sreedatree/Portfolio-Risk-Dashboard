# Download historical stock prices and summarize daily percentage returns.

import yfinance as yf

# Define the stock tickers included in the sample portfolio.
tickers = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ", "XOM"]

# Download historical closing prices for the selected date range.
prices = yf.download(
    tickers,
    start="2022-01-01",
    end="2025-01-01"
)["Close"]

# Calculate day-over-day percentage changes and remove missing observations.
returns = prices.pct_change().dropna()

# Preview the first five rows of calculated daily returns.
print(returns.head())

# Display the mean daily return for each stock over the selected period.
print("\nAverage Daily Returns:")
print(returns.mean())