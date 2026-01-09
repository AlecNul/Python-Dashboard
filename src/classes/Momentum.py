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

    def get_equity_curve(self):
        if self.positions is None:
            self.define_positions()
        
        prices = self.asset.prices.loc[self.start_date:self.end_date]['Price']
        asset_returns = prices.pct_change()
        strategy_returns = self.positions * asset_returns
        
        return self.capital * (1 + strategy_returns.fillna(0)).cumprod()

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

    # Metrics
    # Actually for most metrics we do practically the same as BuyHold, but adapt with equity curve. Inheritance could probably make this easier
    # But not enough time now too much skiing
    def pnl(self):
        """
        Returns the PnL (value and pct)
        """
        equity = self.get_equity_curve()
        start_val = equity.iloc[0]
        end_val = equity.iloc[-1]

        pnl_val = end_val - start_val
        pnl_pct = (end_val - start_val) / start_val
        return pnl_val, pnl_pct
    
    def drawdown(self):
        equity = self.get_equity_curve()
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        max_drawdown = drawdown.min()
        return drawdown, max_drawdown
    
    def annualized_volatility(self):
        """
        Returns the annualized volatility of the strategy
        """
        equity = self.get_equity_curve()
        returns = equity.pct_change().dropna()
        return returns.std() * (252 ** 0.5)

    def sharpe(self, risk_free_rate:float=0.02):
        """
        Returns the Sharpe ratio
        """
        equity = self.get_equity_curve()
        returns = equity.pct_change().dropna()
        excess_return = returns.mean() * 252 - risk_free_rate
        vol = self.annualized_volatility()

        if vol == 0:
            return 0.0
        return excess_return / vol

    def sortino(self, risk_free_rate:float=0.02):
        """
        Returns the Sortino ratio (Penalizes only downside volatility)
        """
        equity = self.get_equity_curve()
        returns = equity.pct_change().dropna()
        negative_returns = returns[returns < 0]
        downside_vol = negative_returns.std() * (252 ** 0.5)
        excess_return = returns.mean() * 252 - risk_free_rate

        if downside_vol == 0:
            return 0.0
        return excess_return / downside_vol

    def historical_VaR(self, confidence_level:float=0.95):
        """
        Returns the Daily Value at Risk (95%)
        """
        equity = self.get_equity_curve()
        returns = equity.pct_change().dropna()

        if returns.empty:
            return 0.0
        
        sorted_returns = returns.sort_values()
        VaR = np.percentile(sorted_returns, (1 - confidence_level) * 100)
        return VaR

    def historical_ES(self, confidence_level:float=0.95):
        """
        Returns the Daily Expected Shortfall (95%)
        """
        equity = self.get_equity_curve()
        returns = equity.pct_change().dropna()
        
        if returns.empty:
            return 0.0

        VaR_threshold = np.percentile(returns, (1 - confidence_level) * 100)
        ES = returns[returns <= VaR_threshold].mean()
        return ES