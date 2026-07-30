import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def apply_dashboard_theme(fig):
    """
    Apply consistent styling to every Plotly chart.
    """

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
    """
    Create an interactive Plotly chart comparing
    portfolio growth against the SPY benchmark.
    """

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


def correlation_heatmap(corr_matrix):
    """
    Create an interactive correlation heatmap.
    """

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
    """
    Create a pie chart of sector allocation.
    """

    df = pd.DataFrame({
        "Sector": allocation.keys(),
        "Weight": allocation.values()
    })

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
    """
    Create a rolling volatility chart.
    """

    fig = px.line(
        rolling_vol,
        title="30-Day Rolling Portfolio Volatility"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Annualized Volatility"
    )

    fig.update_traces(
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Volatility: %{y:.2%}<extra></extra>"
)

    fig = apply_dashboard_theme(fig)
    return fig 


def health_score_gauge(score):
    """
    Create a gauge chart for the portfolio health score.
    """

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