import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class Asset:
    """
    A personalized class based on the Ticker class of yfinance
    """
    # Constructor
    def __init__(self, ticker_symbol:str):
        self.ticker_symbol = ticker_symbol
        try:
            self.ticker = yf.Ticker(ticker_symbol)
            self.history = self.ticker.history(period="max", auto_adjust=True)

            self.prices = self.history[['Close']].rename(columns={'Close': 'Price'})
            self.returns = self.prices['Price'].pct_change().dropna()
            self.log_returns = np.log( self.prices['Price'] / self.prices['Price'].shift(1) ).dropna()
            self.offsets = {
            "1mo": 30, "3mo": 90, "6mo": 180, 
            "1y": 365, "2y": 730, "5y": 1825
        }

        except Exception as e:
            print(f"Error while creating the Asset : {e}")


    # Methods

    # Will be useful for strategies
    def slice(self, data_type:str, start_date:str=None, end_date:str=None):
        """
        Takes two dates (YYYY:MM:DD)
        Returns the data_type between those dates (ex. returns, history...)
        """
        try:
            attribute = getattr(self,data_type)
        except AttributeError:
            print(f"Error : {data_type} is not an attribute of Asset.")

        sliced_df = attribute.loc[start_date:end_date]
        return sliced_df
    
    def handle_duration(self, data, duration:str):
        """
        Takes a period (duration:str) as parameter
        Returns the data sliced according to the duration
        """
        if (duration!="max"):
            # So we don't need to ask yfinance for data again
            today = data.index.max()
            res = data.loc[today-pd.Timedelta(days=self.offsets[duration]):today]
        elif (duration=="max"):
            res = data  
        else: # Ask yfinance again but shouldn't happen as we choose the duration in the ui
            raise ValueError("Duration must be 'max' or a valid key in offsets.")
            # old : data = self.ticker.history(period=duration, auto_adjust=True)
            # old : data = self.ticker.history(period=duration, auto_adjust=True)[['Close']].rename(columns={'Close': 'Price'})
        return res

    def rolling_mean(self, window:int=20):
        """
        Takes a window size as parameter (default 20 days)
        Returns the rolling mean of the prices
        """
        rolling_mean = self.prices.rolling(window=window).mean().rename(columns={'Price': 'Mean'})
        return rolling_mean

    def rolling_std(self, window:int=20):
        """
        Takes a window size as parameter (default 20 days)
        Returns the rolling standard deviation of the prices
        """
        rolling_std = self.log_returns.rolling(window=window).std().rename(columns={'Price': 'Std'})
        return rolling_std

    # Graphics
    def candle_graph(self, duration:str="max"):
        """
        Takes a period (duration:str) as parameter
        Returns a candle graph of the prices
        """
        data = self.handle_duration(self.history[['Open','High','Low','Close']], duration)

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
        # Dynamic title according to period
        fig.update_layout(
            title=f"{self.ticker_symbol} - Period : {duration}",
            yaxis_title="Price ($)",
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        return fig

    def price_graph(self, duration:str="max"):
        """
        Returns a line graph of the prices
        """
        data = self.handle_duration(self.prices, duration)

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Price'],
                mode='lines',
                name=self.ticker_symbol
            )
        )
        fig.update_layout(
            title=f"{self.ticker_symbol} - Period : {duration}",
            yaxis_title="Price ($)",
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        return fig

    # Could merge add_rolling_mean and add_rolling_std into one method with an argument but for now it's ok

    def add_rolling_mean(self, fig, duration:str="max", w:int=20):
        """
        Adds rolling mean to an existing figure
        """
        rolling_mean = self.rolling_mean(window=w)
        data = self.handle_duration(rolling_mean, duration)

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Mean'],
            mode='lines',
            name=f'20-Day Rolling Mean'))
        return fig
    
    def add_rolling_std(self, fig, duration:str="max", w:int=20):
        """
        Adds rolling standard deviation to an existing figure
        """
        rolling_std = self.rolling_std(window=w)
        data = self.handle_duration(rolling_std, duration)

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Std'],
            mode='lines',
            name=f'20-Day Rolling Std'))
        return fig