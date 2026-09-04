import streamlit as st
import pandas as pd
from data_loader import load_prices
from risk_metrics import calculate_risk_metrics
from charts import portfolio_growth_chart
from charts import correlation_heatmap
from charts import sector_allocation_chart
from charts import rolling_volatility_chart
from insights import generate_insights
from stock_info import get_stock_info
from health_score import calculate_health_score
from calculations import calculate_portfolio_growth
from calculations import calculate_correlation
from calculations import calculate_sector_allocation
from calculations import calculate_rolling_volatility
from calculations import calculate_stock_performance
from executive_summary import generate_executive_summary

def section_header(title, caption):
    st.subheader(title)
    st.caption(caption)

st.set_page_config(
    page_title="Portfolio Risk Dashboard",
    layout="wide"
)

st.title("Portfolio Risk Dashboard")
st.caption(
    "Analyze portfolio performance, risk, diversification, and sector exposure using live market data."
)
st.divider()

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


st.sidebar.header("Portfolio Builder")

default_tickers = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ", "XOM"]

reset_col, add_col = st.sidebar.columns(2)

with reset_col:
    if st.button("🔄 Reset"):
        st.session_state.portfolio = default_tickers.copy()
        st.rerun()

if "portfolio" not in st.session_state:
    st.session_state.portfolio = default_tickers.copy()

if "new_ticker" not in st.session_state:
    st.session_state.new_ticker = ""

new_ticker_input = st.sidebar.text_input("Add Stock", key="new_ticker")

if st.sidebar.button("Add"):
    ticker_to_add = new_ticker_input.strip().upper()
    if ticker_to_add == "":
        pass
    elif ticker_to_add in st.session_state.portfolio:
        st.sidebar.error(f"Ticker '{ticker_to_add}' is already in the portfolio.")
    else:
        validation_info = get_stock_info([ticker_to_add])
        if validation_info and validation_info[0]["Company"] != "Invalid Ticker":
            st.session_state.portfolio.append(ticker_to_add)
            st.session_state.new_ticker = ""
            st.experimental_rerun()
        else:
            st.sidebar.error(f"Ticker '{ticker_to_add}' is invalid.")

st.sidebar.divider()

st.sidebar.markdown("### Current Holdings")

stock_info = get_stock_info(st.session_state.portfolio)

for ticker in st.session_state.portfolio.copy():
    company_name = next((item["Company"] for item in stock_info if item["Ticker"] == ticker), "Unknown Company")
    col1, col2 = st.sidebar.columns([6, 1])
    col1.markdown(
    f'<span title="{company_name}"><strong>{ticker}</strong></span>',
    unsafe_allow_html=True,
)

    if col2.button("✕", key=f"remove_{ticker}", type="secondary"):
        st.session_state.portfolio.remove(ticker)
        st.experimental_rerun()

tickers = st.session_state.portfolio

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

st.sidebar.markdown("#### Normalized Allocation")

for ticker, weight in zip(tickers, weights):
    st.sidebar.caption(f"{ticker}: **{weight:.1%}**")

with st.spinner("📈 Loading market data..."):

    try:

        prices = load_prices(
            tickers,
            start_date=f"{start_year}-01-01",
            end_date=f"{end_year}-01-01"
        )

        portfolio_growth = calculate_portfolio_growth(
            prices,
            weights,
            start_date=f"{start_year}-01-01",
            end_date=f"{end_year}-01-01"
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

    except Exception as e:

        st.error(
            "Unable to load market data. Please check your internet connection or try again."
        )

        st.exception(e)

        st.stop()

st.sidebar.divider()

st.sidebar.info(
    """
    **Portfolio Risk Dashboard**

    This application analyzes historical portfolio performance using professional financial metrics including annual return, volatility, Sharpe Ratio, Beta, and Maximum Drawdown.

    Data Source: Yahoo Finance
    """
)

section_header(
    "Portfolio Metrics",
    "Key performance and risk metrics calculated from historical returns."
)

portfolio_return = portfolio_growth["portfolio"].iloc[-1] - 1
benchmark_return = portfolio_growth["benchmark"].iloc[-1] - 1
outperformance = portfolio_return - benchmark_return

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Portfolio Return",
    f"{portfolio_return:.2%}"
)

col2.metric(
    "S&P 500 Return",
    f"{benchmark_return:.2%}"
)

col3.metric(
    "Outperformance",
    f"{outperformance:.2%}"
)

col4.metric(
    "Sharpe Ratio",
    f"{metrics['Sharpe Ratio']:.2f}"
)

col5.metric(
    "Max Drawdown",
    f"{metrics['Max Drawdown']:.2%}",
    help="Largest percentage decline from a previous portfolio peak."
)

sector_allocation = calculate_sector_allocation(
    stock_info,
    weights
)

section_header(
    "Portfolio Summary",
    "Highlights of your portfolio's strongest and weakest performers."
)

best_stock = stock_performance.loc[
    stock_performance["Total Return"].idxmax()
]

worst_stock = stock_performance.loc[
    stock_performance["Total Return"].idxmin()
]

largest_holding = stock_performance.loc[
    stock_performance["Weight"].idxmax()
]

largest_sector = max(
    sector_allocation.items(),
    key=lambda x: x[1]
)

summary1, summary2, summary3, summary4 = st.columns(4)

summary1.metric(
    "Best Performer",
    best_stock["Ticker"],
    f"{best_stock['Total Return']:.2%}"
)

summary2.metric(
    "Worst Performer",
    worst_stock["Ticker"],
    f"{worst_stock['Total Return']:.2%}"
)

summary3.metric(
    "Largest Holding",
    largest_holding["Ticker"],
    f"{largest_holding['Weight']:.1%}"
)

summary4.metric(
    "Largest Sector",
    largest_sector[0],
    f"{largest_sector[1]:.1%}"
)

st.divider()

rolling_vol = calculate_rolling_volatility(
    prices,
    weights
)
insights = generate_insights(
    metrics,
    sector_allocation
)

health = calculate_health_score(
    metrics,
    sector_allocation,
    weights
)

executive = generate_executive_summary(
   metrics,
   health,
   best_stock,
   largest_sector,
   largest_holding
)

section_header(
    "📋 Executive Summary",
    "A high-level overview of your portfolio's performance, risk, and diversification."
)

with st.container(border=True):

    st.markdown(executive["summary"])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏆 Key Highlights")

        st.write(f"**Best Performer:** {executive['best_stock']} ({executive['best_return']:.2%})")
        st.write(f"**Largest Sector:** {executive['largest_sector']} ({executive['sector_weight']:.1%})")

    with col2:
        st.markdown("#### ❤️ Portfolio Health")

        st.write(f"**Health Grade:** {health['grade']}")
        st.write(f"**Risk Level:** {health['risk']}")

section_header(
    "Portfolio Visualizations",
    "Interactive charts showing portfolio growth, correlations, and sector exposure."
)

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

st.subheader("Portfolio Holdings")

display_df = stock_performance.copy()

display_df["Weight"] = display_df["Weight"].map(
    lambda x: f"{x:.1%}"
)

display_df["Total Return"] = display_df["Total Return"].map(
    lambda x: f"{x:.2%}"
)

display_df = display_df.merge(
    pd.DataFrame(stock_info),
    on="Ticker"
)

display_df = display_df[
    [
        "Company",
        "Ticker",
        "Sector",
        "Weight",
        "Total Return"
    ]
]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

st.divider()

section_header(
    "Portfolio Health",
    "Evaluate the overall quality of your portfolio."
)

with st.container(border=True):
    # Overall Score
    score_col1, score_col2 = st.columns([1, 3])

    with score_col1:
        st.metric(
            "Overall Score",
            f"{health['score']}/100"
        )

    with score_col2:

        metric1, metric2 = st.columns(2)

        metric1.metric(
            "Grade",
            health["grade"]
        )

        metric2.metric(
            "Risk",
            health["risk"]
        )

    st.divider()

    st.markdown("### Strengths")

    st.divider()

st.markdown("### Recommendations")

recommendations = []

if largest_holding["Weight"] > 0.35:
    recommendations.append(
        f"Reduce exposure to {largest_holding['Ticker']} to improve diversification."
    )

if largest_sector[1] > 0.50:
    recommendations.append(
        f"Technology concentration is high. Consider adding holdings in other sectors."
    )

if metrics["Beta"] > 1.2:
    recommendations.append(
        "Portfolio volatility is above the overall market."
    )

if metrics["Sharpe Ratio"] < 1:
    recommendations.append(
        "Look for investments with stronger risk-adjusted returns."
    )

if not recommendations:
    recommendations.append(
        "Your portfolio appears well balanced. No major concerns detected."
    )

for recommendation in recommendations:
    st.warning(recommendation)

    for item in health["insights"]:
        st.success(item)

section_header(
    "Market Insights",
    "Automatically generated observations based on your portfolio analytics."
)

for insight in insights:
    st.info(insight)

st.divider()

st.caption(
    "Portfolio Risk Dashboard v3.1 Beta\n\n"
    "Built with Python • Streamlit • Plotly • Pandas • yfinance"
)