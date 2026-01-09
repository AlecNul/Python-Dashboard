import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class Asset:
    """
    A personalized class based on the Ticker class of yfinance
    """
    # Constructor
    def __init__(self, ticker_symbol:str, start_date:str=None, end_date:str=None):
        self.ticker_symbol = ticker_symbol
        self.start_date = start_date
        self.end_date = end_date
        
        try:
            self.ticker = yf.Ticker(ticker_symbol)
            if start_date and end_date:
                self.history = self.ticker.history(start=start_date, end=end_date, auto_adjust=True)
            else:
                self.history = self.ticker.history(period="max", auto_adjust=True)

            self.prices = self.history[['Close']].rename(columns={'Close': 'Price'})
            self.returns = self.prices['Price'].pct_change().dropna()
            self.log_returns = np.log( self.prices['Price'] / self.prices['Price'].shift(1) ).dropna()

        except Exception as e:
            print(f"Error while creating the Asset : {e}")

    def rolling_mean(self, window:int=20):
        """
        Takes a window size as parameter (default 20 days)
        Returns the rolling mean of the prices
        """
        rolling_mean = self.prices.rolling(window).mean().rename(columns={'Price': 'Mean'})
        return rolling_mean

    def rolling_std(self, window:int=20):
        """
        Takes a window size as parameter (default 20 days)
        Returns the rolling standard deviation of the prices
        """
        rolling_std_series = self.log_returns.rolling(window=window).std() 
        rolling_std = rolling_std_series.to_frame(name='Std') 
        return rolling_std
        return rolling_std
    
    # I'll try to do some EVT
    def get_hill_estimator(self):
        """
        Returns the estimated ksi using the Hill estimator
        """
        # I'll focus on extreme losses.
        losses = -self.returns[self.returns < 0].dropna()
        if len(losses) < 10:
            return pd.Series(dtype='float64')
        sorted_losses = np.sort(losses.values)[::-1]

        # Then, for the k(n), we'll try different values, from 2 to 20% of the total count
        hill_values = []
        max_k = int(len(sorted_losses) * 0.2)
        k_values = range(2, max_k)

        for k in k_values:
            selection = sorted_losses[:k]
            threshold = sorted_losses[k-1]
            
            log_diff = np.log(selection) - np.log(threshold)
            ksi = np.mean(log_diff) # The sum and division by k is here
            hill_values.append(ksi)

        return pd.Series(data=hill_values, index=k_values)

    # Graphics
    def candle_graph(self):
        """
        Returns a candle graph of the prices
        """
        data = self.history[['Open','High','Low','Close']]

        fig = go.Figure()
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=self.ticker_symbol
            )
        )
        
        title_text = f"{self.ticker_symbol}"
        if self.start_date and self.end_date:
            title_text += f" ({self.start_date} - {self.end_date})"

        fig.update_layout(
            title=title_text,
            yaxis_title="Price ($)",
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        return fig

    def price_graph(self):
        """
        Returns a line graph of the prices
        """
        data = self.prices

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Price'],
                mode='lines',
                name=self.ticker_symbol
            )
        )
        
        title_text = f"{self.ticker_symbol}"
        if self.start_date and self.end_date:
            title_text += f" ({self.start_date} - {self.end_date})"

        fig.update_layout(
            title=title_text,
            yaxis_title="Price ($)",
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        return fig

    # Could merge add_rolling_mean and add_rolling_std into one method with an argument but for now it's ok

    def add_rolling_mean(self, fig, w:int=20):
        """
        Adds rolling mean to an existing figure
        """
        rolling_mean = self.rolling_mean(window=w)
        
        fig.add_trace(go.Scatter(
            x=rolling_mean.index,
            y=rolling_mean['Mean'],
            mode='lines',
            name=f'{w}-Day Rolling Mean'))
        return fig

    def add_rolling_std(self, fig, w:int=20):
        """
        Adds rolling standard deviation to an existing figure
        """
        rolling_std = self.rolling_std(window=w)

        fig.add_trace(go.Scatter(
            x=rolling_std.index,
            y=rolling_std['Std'],
            mode='lines',
            name=f'{w}-Day Rolling Std',
            yaxis='y2'))
        
        # Need to update axis else it's uninterpretable
        fig.update_layout(
            yaxis=dict(
                title="Price ($)",
                side="left"
            ),
            yaxis2=dict(
                title=f"{w}-Day Rolling Std",
                anchor="x",
                overlaying="y",
                tickformat=".1%", 
                side="right"
            )
        )

        return fig