import numpy as np
import pandas as pd
from classes.Asset import Asset
import plotly.graph_objects as go

class Momentum:
    """
    This class is a Trade-based strategy, which will use rolling mean to determine best dates to buy and sell an Asset.
    """
    # Constructor
    def __init__(self, asset:Asset, start:str, end:str, cap:float=1000):
        self.asset = asset
        self.start_date = start
        self.end_date = end
        self.capital = cap
        self.positions = None

    # Method (Finding best trades)
    def define_positions(self,w:int=10):

        prices = self.asset.prices.loc[self.start_date:self.end_date]
        rolling_mean = self.asset.rolling_mean(w,start_date=self.start_date, end_date=self.end_date) 
        signal = np.where(prices['Price']>rolling_mean['Mean'], 1.0, 0.0)

        self.positions = pd.Series(data=signal, index=prices.index).shift(1) # shift so if we decide to buy at time t, at time t+1, we're (1) 
        self.positions.fillna(0.0, inplace=True) # we have it bc we bought it just before the close 

    def capital_graph(self):
        """
        Creates a graph that displays the capital over time, following the strategy
        """

        self.define_positions()
        prices = self.asset.prices.loc[self.start_date:self.end_date]['Price']
        asset_returns = prices.pct_change()
        strategy_returns = self.positions * asset_returns
        values = self.capital * (1 + strategy_returns.fillna(0)).cumprod()

        start_val = values[0]
        end_val = values[-1]
        color = "#00C805" if end_val >= start_val else "#FF3B30"

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=values.index,
            y=values,
            mode='lines',
            name='Capital Value',
            line=dict(color=color, width=2),
        ))

        # Comparison with initial capital
        fig.add_hline(y=self.capital, line_dash="dash", line_color="gray", annotation_text="Initial Capital")

        fig.update_layout(
            title="Equity Curve (Buy & Hold)",
            yaxis_title="Capital Value ($)",
            xaxis_title="Date",
            template="plotly_dark",
            hovermode="x unified"
        )
        return fig

    def pnl(self):
        """
        Returns the PnL (value and pct)
        """
        # In case start or end date are not trading days
        end_price = self.prices.iloc[-1]
        start_price = self.prices.iloc[0]
        pct = (end_price-start_price) / start_price
        return pct*self.capital, pct