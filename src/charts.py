# Plotly visualizations for portfolio performance, diversification, and risk.

import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


def apply_dashboard_theme(fig):
    """Apply consistent typography, spacing, legends, and axes to a Plotly figure."""

    # Standardize chart layout so dashboard visuals share a consistent appearance.
    fig.update_layout(
        template="plotly_white",
        font=dict(
            family="Inter, Arial, sans-serif",
            size=14
        ),
        title=dict(
            x=0.02,
            font=dict(size=20)
        ),
        legend=dict(
            orientation="h",
            y=1.08,
            x=1,
            xanchor="right"
        ),
        margin=dict(
            l=30,
            r=30,
            t=70,
            b=30
        ),
        hovermode="x unified"
    )

    fig.update_xaxes(showgrid=False)

    fig.update_yaxes(
        gridcolor="#EAEAEA"
    )

    return fig


def portfolio_growth_chart(portfolio_growth):
    """Plot normalized portfolio growth against the S&P 500 (SPY) benchmark."""

    # Combine portfolio and benchmark series for a shared time-axis comparison.
    df = pd.DataFrame({
        "Portfolio": portfolio_growth["portfolio"],
        "S&P 500 (SPY)": portfolio_growth["benchmark"]
    })

    fig = px.line(
        data_frame=df,
        x=df.index,
        y=df.columns,
        title="Portfolio Performance vs. S&P 500"
    )

    # Use a dashed benchmark line to distinguish it from the portfolio.
    fig.update_traces(
        selector=dict(name="S&P 500 (SPY)"),
        line=dict(dash="dash")
    )

    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>%{x|%b %d, %Y}<br>Growth: %{y:.2f}×<extra></extra>"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Growth (Normalized)",
        legend_title="Performance",
        hovermode="x unified"
    )

    fig = apply_dashboard_theme(fig)
    return fig


def portfolio_comparison_chart(growth_a, growth_b):
    """Compare cumulative growth trajectories for two portfolios."""

    fig = go.Figure()

    # Plot both portfolios as separate traces on the same timeline.
    fig.add_trace(
        go.Scatter(
            x=growth_a.index,
            y=growth_a,
            mode="lines",
            name="Portfolio A"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=growth_b.index,
            y=growth_b,
            mode="lines",
            name="Portfolio B"
        )
    )

    fig.update_layout(
        title="Portfolio A vs. Portfolio B",
        xaxis_title="Date",
        yaxis_title="Normalized Growth",
        hovermode="x unified"
    )

    return fig


def correlation_heatmap(corr_matrix):
    """Visualize pairwise asset-return correlations on a scale from -1 to 1."""

    # Fix the color range so correlation strengths remain comparable.
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Asset Correlation Heatmap"
    )

    fig.update_layout(
        xaxis_title="Assets",
        yaxis_title="Assets"
    )

    fig.update_traces(
        hovertemplate="Correlation: %{z:.2f}<extra></extra>"
    )

    fig = apply_dashboard_theme(fig)
    return fig


def sector_allocation_chart(allocation):
    """Show the proportion of portfolio weight allocated to each sector."""

    df = pd.DataFrame({
        "Sector": allocation.keys(),
        "Weight": allocation.values()
    })

    # Label slices with both sector names and allocation percentages.
    fig = px.pie(
        df,
        names="Sector",
        values="Weight",
        title="Portfolio Sector Allocation"
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Weight: %{percent}<extra></extra>"
    )

    fig = apply_dashboard_theme(fig)
    return fig


def rolling_volatility_chart(rolling_vol):
    """Plot annualized rolling volatility across the selected period."""

    fig = px.line(
        rolling_vol,
        title="30-Day Rolling Portfolio Volatility"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Annualized Volatility"
    )

    # Format hover values as percentages for readability.
    fig.update_traces(
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Volatility: %{y:.2%}<extra></extra>"
    )

    fig = apply_dashboard_theme(fig)
    return fig


def health_score_gauge(score):
    """Display a portfolio health score on a color-banded 0–100 gauge."""

    # Color bands distinguish lower and higher health-score ranges.
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"thickness": 0.3},
                "steps": [
                    {"range": [0, 50], "color": "#ef4444"},
                    {"range": [50, 70], "color": "#f59e0b"},
                    {"range": [70, 85], "color": "#84cc16"},
                    {"range": [85, 100], "color": "#22c55e"},
                ],
            },
        )
    )

    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    return apply_dashboard_theme(fig)


def risk_profile_chart(metrics):
    """Display selected risk indicators in a horizontal bar chart."""

    # Convert percentage-based risk measures to percentage points for display.
    # Beta is unitless, so bar lengths across metrics are not directly comparable.
    risk_metrics = {
        "Volatility": metrics["Volatility"] * 100,
        "Beta": metrics["Beta"],
        "Maximum Drawdown": abs(metrics["Max Drawdown"]) * 100,
        "Value at Risk": abs(metrics["Value at Risk"]) * 100
    }

    fig = go.Figure()

    # Label each bar with its numeric value to aid interpretation.
    fig.add_trace(
        go.Bar(
            x=list(risk_metrics.values()),
            y=list(risk_metrics.keys()),
            orientation="h",
            text=[
                f"{value:.2f}"
                for value in risk_metrics.values()
            ],
            textposition="auto"
        )
    )

    fig.update_layout(
        title="Portfolio Risk Profile",
        xaxis_title="Metric Value (mixed units)",
        yaxis_title="",
        template="plotly_white",
        height=350
    )

    return fig