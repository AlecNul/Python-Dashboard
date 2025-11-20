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

        except Exception as e:
            print(f"Error while creating the Asset : {e}")


    # Methods
    def slice_history(self, start_date:str=None, end_date:str=None):
        """
        Takes two dates (YYYY:MM:DD)
        Returns the history between those dates
        """
        sliced_df = self.history[start_date:end_date]
        return sliced_df

    # Graphics
    def candle_graph(self, duration:str="max"):
        """
        Takes a period (duration:str) as parameter
        Returns a candle graph of the prices
        """

        offsets = {
            "1mo": 30, "3mo": 90, "6mo": 180, 
            "1y": 365, "2y": 730, "5y": 1825
        }

        data = self.history
        if (duration!="max"):
            # So we don't need to ask yfinance for data again
            today = self.history.index.max()
            data = self.history.loc[today-pd.Timedelta(days=offsets[duration]):today]  
        else:
            # Shouldn't happen as we choose the duration in the main
            data = self.ticker.history(period=duration, auto_adjust=True)

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=self.ticker_symbol
        ))

        # Dynamic title according to period
        fig.update_layout(
            title=f"{self.ticker_symbol} - Period : {duration}",
            yaxis_title="Price ($)",
            template="plotly_dark",
            xaxis_rangeslider_visible=False
        )
        
        return fig