import yfinance as yf

# List of stocks
tickers = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ", "XOM"]

# Download closing prices
prices = yf.download(
    tickers,
    start="2022-01-01",
    end="2025-01-01"
)["Close"]

# Calculate daily percentage returns
returns = prices.pct_change().dropna()

print(returns.head())

print("\nAverage Daily Returns:")
print(returns.mean())