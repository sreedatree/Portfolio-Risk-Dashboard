import streamlit as st
from data_loader import load_prices
from calculations import calculate_portfolio_growth
from calculations import calculate_correlation
from risk_metrics import calculate_risk_metrics
from charts import portfolio_growth_chart
from charts import correlation_heatmap
from calculations import calculate_sector_allocation
from charts import sector_allocation_chart
from calculations import calculate_rolling_volatility
from charts import rolling_volatility_chart
from insights import generate_insights
from calculations import calculate_stock_performance


st.set_page_config(
    page_title="Portfolio Risk Dashboard",
    layout="wide"
)

st.title("📊 Portfolio Risk Dashboard")
st.caption(
    "Analyze portfolio performance, risk, diversification, and sector exposure using live market data."
)
st.divider()

st.sidebar.markdown("## ⚙️ Dashboard Controls")
st.sidebar.header("Portfolio Settings")

start_year = st.sidebar.selectbox(
    "Start Year",
    [2022, 2023, 2024],
    index=0
)

end_year = st.sidebar.selectbox(
    "End Year",
    [2023, 2024, 2025],
    index=2
)

if start_year >= end_year:
    st.error("The end year must be after the start year.")
    st.stop()


st.sidebar.subheader("Portfolio")

ticker_input = st.sidebar.text_input(
    "Enter stock tickers (comma-separated)",
    value="AAPL, MSFT, NVDA, JPM, JNJ, XOM"
)

tickers = [
    ticker.strip().upper()
    for ticker in ticker_input.split(",")
    if ticker.strip()
]

default_weight = 1 / len(tickers)

weights = []

for ticker in tickers:
    weight = st.sidebar.slider(
        ticker,
        min_value=0.0,
        max_value=1.0,
        value=float(default_weight),
        step=0.01
    )
    weights.append(weight)

total_weight = sum(weights)

if total_weight == 0:
    st.sidebar.error("Please give at least one stock a weight greater than 0.")
    st.stop()

weights = [w / total_weight for w in weights]

st.sidebar.write("Normalized Portfolio Weights")
for ticker, weight in zip(
    tickers,
    weights
):
    st.sidebar.write(f"{ticker}: {weight:.1%}")

prices = load_prices(
    tickers,
    start_date=f"{start_year}-01-01",
    end_date=f"{end_year}-01-01"
)

portfolio_growth = calculate_portfolio_growth(
    prices,
    weights
)

corr_matrix = calculate_correlation(prices)

metrics = calculate_risk_metrics(
    prices,
    start_date=f"{start_year}-01-01",
    end_date=f"{end_year}-01-01",
    weights=weights
)

stock_performance = calculate_stock_performance(
    prices,
    tickers,
    weights
)

st.sidebar.divider()

st.sidebar.info(
    """
    **Portfolio Risk Dashboard**

    This application analyzes historical portfolio performance using professional financial metrics including annual return, volatility, Sharpe Ratio, Beta, and Maximum Drawdown.

    Data Source: Yahoo Finance
    """
)

st.subheader("📈 Portfolio Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Annual Return",
    f"{metrics['Annual Return']:.2%}"
)

col2.metric(
    "Volatility",
    f"{metrics['Volatility']:.2%}"
)

col3.metric(
    "Sharpe Ratio",
    f"{metrics['Sharpe Ratio']:.2f}"
)

col4.metric(
    "Beta",
    f"{metrics['Beta']:.2f}",
    help="Measures how sensitive the portfolio is to movements in the overall market. A beta of 1 means it tends to move with the market."
)

col5.metric(
    "Max Drawdown",
    f"{metrics['Max Drawdown']:.2%}",
    help="Largest percentage decline from a previous portfolio peak."
)

sector_allocation = calculate_sector_allocation(
    tickers,
    weights
)
rolling_vol = calculate_rolling_volatility(
    prices,
    weights
)
insights = generate_insights(
    metrics,
    sector_allocation
)

st.subheader("📊 Portfolio Visualizations")

col_left, col_right = st.columns(2)

with col_left:
    growth_fig = portfolio_growth_chart(portfolio_growth)
    st.plotly_chart(growth_fig, use_container_width=True)

with col_right:
    heatmap_fig = correlation_heatmap(corr_matrix)
    st.plotly_chart(heatmap_fig, use_container_width=True)

st.divider()

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    sector_fig = sector_allocation_chart(sector_allocation)
    st.plotly_chart(
        sector_fig,
        use_container_width=True
    )

with bottom_right:
    vol_fig = rolling_volatility_chart(rolling_vol)
    st.plotly_chart(
        vol_fig,
        use_container_width=True
    )

st.divider()


st.subheader("💡 Portfolio Insights")

for insight in insights:
    st.info(insight)

st.divider()

st.caption(
    "Built with Python • Streamlit • Plotly • Pandas • yfinance"
    )