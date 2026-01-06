from classes.Asset import Asset
import pandas as pd
import numpy as np
import plotly.graph_objects as go

"""
Actually, we should wonder, if our dashboard is going to update every 5 minutes, we may want to know each time the perf of our portfolio so far. 
So the start_date, end_date method won't be always the best one (actually very good for backtesting strategies). 
But how to keep it up to date ? -> We'll have to make an update method in every class, so that we don't restart from the beginning each time

Also, maybe we want every strategy to inherit from a base Strategy class (BuyHold actually) bc the metrics formula are always the same, we'll just have to change the returns and the prices and the start/end date will become lists.
Every strategy is basically a BuyHold, but with a vector of start and end positions.

Btw, I'm constructing the strategy around 1 Asset (given the instructions), 
So I assume, in the Backtesting part, we choose a list of tickers,
and then we backtest on them.
-> So I think Backtest() should be a method of a portfolio, bc in the portfolio we choose the tickers.
Something like portfolio.backtest(Strategy)

However, I wonder if this is suitable for any kind of strategy ? I think we should refine the definition of strategy :
Let's say there's Asset-based strategies (buyhold, momentum...) and Portfolio-based strategies which focus on weighing multiple Assets the right way.

-> Gives idea for a ML process that may give a rating/evaluation to an Asset, based on different metrics, 
in order to advise the Portfolio-based strategies.
"""

class BuyHold:
    # Constructor
    def __init__(self, asset:Asset, start:str, end:str, cap:float=1000):
        self.asset = asset
        self.start_date = start
        self.end_date = end
        self.capital = cap

        self.returns = self.asset.returns.loc[self.start_date:self.end_date]
        self.log_returns = self.asset.log_returns.loc[self.start_date:self.end_date]
        self.prices = self.asset.prices.loc[self.start_date:self.end_date]

    '''
    # Update Method
    def update(self):
        self.end_date=
    '''
    # Methods (Metrics)
    def pnl(self):
        """
        Returns the PnL (value and pct)
        """
        # In case start or end date are not trading days
        end_price = self.prices.iloc[-1]
        start_price = self.prices.iloc[0]
        pct = (end_price-start_price) / start_price
        return pct*self.capital, pct

    # Graph
    def capital_graph(self):
        """
        Creates a graph that displays the capital over time, following the strategy
        """

        values = self.prices['Price'] * self.capital/self.prices['Price'].iloc[0]
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
    def drawdown(self):
        """
        Returns the drawdown series and the max drawdown (tuple)
        """
        cummax = self.prices.cummax()
        drawdown = (self.prices - cummax) / cummax
        max_drawdown = drawdown.min()
        return drawdown, max_drawdown

    # Note : For the annualized volatility we always assume that vola at t and at t-1 are independent, however it's not true.
    # Implementing GARCH model could be a good idea for better estimates.
    # https://www.investopedia.com/terms/g/garch.asp
    # https://cdn.prod.website-files.com/688125a82bfc6e536cc30914/689432dd1a3c31ee70d9398c_GARCH.pdf 

    def annualized_volatility(self):
        """
        Returns the annualized volatility
        """
        vol = self.returns.std() * (252 ** 0.5)
        return vol
    
    def downside_volatility(self):
        """
        Returns the annualized downside volatility
        """
        negative_returns = self.log_returns[self.log_returns < 0]
        downside_vol = negative_returns.std() * (252 ** 0.5)
        return downside_vol

    def sharpe(self, risk_free_rate:float=0.02):
        """
        Takes the risk free rate as parameter (default 2% ?)
        Returns the Sharpe ratio
        """
        excess_return = self.returns.mean()*252 - (risk_free_rate)
        sharpe_ratio = excess_return / self.annualized_volatility()
        return sharpe_ratio
    
    def sortino(self, risk_free_rate:float=0.02):
        """
        Takes the risk free rate as parameter (default 2% ?)
        Returns the Sortino ratio
        """
        excess_return = self.returns.mean()*252 - (risk_free_rate)
        sortino_ratio = excess_return / self.downside_volatility()
        return sortino_ratio
    
    def historical_VaR(self, confidence_level:float=0.95):
        """
        Takes the confidence level as parameter (default 95%)
        Returns the Value at Risk (for all the period between end and start date)
        """
        historical_returns = self.asset.returns.loc[:self.start_date]
        sorted_returns = historical_returns.sort_values()
        VaR = np.percentile(sorted_returns, (1 - confidence_level) * 100)
        T = len(self.returns)
        return -VaR*(T**0.5) 

    def historical_ES(self, confidence_level:float=0.95):
        """
        Takes the confidence level as parameter (default 95%)
        Returns the Expected Shortfall (for all the period between end and start date)
        """
        historical_returns = self.asset.returns.loc[:self.start_date]
        sorted_returns = historical_returns.sort_values()
        VaR_threshold = np.percentile(sorted_returns, (1 - confidence_level) * 100)
        
        ES = sorted_returns[sorted_returns <= VaR_threshold].mean()
        T = len(self.returns)
        return -ES*(T**0.5)