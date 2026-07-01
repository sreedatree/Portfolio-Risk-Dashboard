import plotly.express as px
import pandas as pd

def portfolio_growth_chart(portfolio_growth):
    """
    Create an interactive Plotly chart showing portfolio growth.
    """

    fig = px.line(
        portfolio_growth,
        title="Portfolio Growth Over Time"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Portfolio Value"
    )

    return fig

import plotly.express as px

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
        title="Sector Allocation"
    )

    fig.update_traces(textposition="inside")

    return fig

def rolling_volatility_chart(rolling_vol):
    """
    Create a rolling volatility chart.
    """

    fig = px.line(
        rolling_vol,
        title="30-Day Rolling Volatility"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Annualized Volatility"
    )

    return fig