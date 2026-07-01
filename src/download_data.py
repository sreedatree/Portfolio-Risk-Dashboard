import yfinance as yf

# List of stocks in our portfolio
tickers = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ", "XOM"]

# Download historical stock prices
prices = yf.download(
    tickers,
    start="2022-01-01",
    end="2025-01-01"
)["Close"]

# Display the first five rows
print(prices.head())

# Dataset information
print("\nDataset Shape:")
print(prices.shape)

print("\nColumn Names:")
print(prices.columns)

print("\nSummary Statistics:")
print(prices.describe())