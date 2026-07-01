import streamlit as st
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

st.sidebar.subheader("Portfolio Weights")
aapl = st.sidebar.slider("AAPL", 0.0, 1.0, 0.25, 0.01)
msft = st.sidebar.slider("MSFT", 0.0, 1.0, 0.20, 0.01)
nvda = st.sidebar.slider("NVDA", 0.0, 1.0, 0.15, 0.01)
jpm = st.sidebar.slider("JPM", 0.0, 1.0, 0.15, 0.01)
jnj = st.sidebar.slider("JNJ", 0.0, 1.0, 0.15, 0.01)
xom = st.sidebar.slider("XOM", 0.0, 1.0, 0.10, 0.01)

weights = [aapl, msft, nvda, jpm, jnj, xom]

total_weight = sum(weights)

if total_weight == 0:
    st.sidebar.error("Please give at least one stock a weight greater than 0.")
    st.stop()

weights = [w / total_weight for w in weights]

st.sidebar.write("Normalized Portfolio Weights")
for ticker, weight in zip(["AAPL", "MSFT", "NVDA", "JPM", "JNJ", "XOM"], weights):
    st.sidebar.write(f"{ticker}: {weight:.1%}")

portfolio_growth = calculate_portfolio_growth(
    start_date=f"{start_year}-01-01",
    end_date=f"{end_year}-01-01",
    weights=weights
)

corr_matrix = calculate_correlation(
    start_date=f"{start_year}-01-01",
    end_date=f"{end_year}-01-01"
)

metrics = calculate_risk_metrics(
    start_date=f"{start_year}-01-01",
    end_date=f"{end_year}-01-01",
    weights=weights
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

sector_allocation = calculate_sector_allocation(weights)
rolling_vol = calculate_rolling_volatility(
    start_date=f"{start_year}-01-01",
    end_date=f"{end_year}-01-01",
    weights=weights
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
    "Built with Python, Streamlit, Plotly, Pandas, and yfinance."
)