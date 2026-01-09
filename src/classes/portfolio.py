#############################
# QUANT B - PORTFOLIO MODULE
#############################



import numpy as np
import pandas as pd
from .Asset import Asset


class Portfolio:
    """
    Simple multi-asset portfolio built from the Asset class.
    """

    def __init__(self, name : str= "Default Portfolio"):
        self.name = name
        self.assets = {}      # {ticker: Asset}
        self.weights = {}     # {ticker: weight}

    # -------------------------------------------------------
    # ASSET MANAGEMENT
    # -------------------------------------------------------

    def add_asset(self, ticker: str, weight: float | None = None):
        """Adds an asset to the portfolio"""
        self.assets[ticker] = Asset(ticker)
        self.weights[ticker] = weight

    def set_equal_weights(self):
        n = len(self.assets)
        if n == 0:
            raise ValueError("Portfolio is empty.")
        for t in self.assets:
            self.weights[t] = 1 / n

    def set_custom_weights(self, weights: dict[str, float]):
        for t in self.assets:
            if t not in weights:
                raise ValueError(f"Missing weight for {t}")
        self.weights = dict(weights)

    def check_weights(self, tol=1e-6):
        weights = list(self.weights.values())
        if any(w is None for w in weights):
            raise ValueError("Some weights are None. Set them first.")
        total = sum(weights)
        return abs(total - 1) < tol


    # -------------------------------------------------------
    # INTERNAL HELPERS
    # -------------------------------------------------------

    def _returns_df(self) -> pd.DataFrame:
        
        returns_list = []

        for ticker, asset in self.assets.items():
            r = asset.returns.rename(ticker)
            returns_list.append(r)

        # Aligns all returns on common dates
        df = pd.concat(returns_list, axis=1, join="inner").dropna()
        return df

    def _weights_vector(self, columns):
        """Returns a numpy array of weights aligned with DataFrame columns"""
        w = np.array([self.weights[c] for c in columns], dtype=float)
        if np.any(np.isnan(w)):
            raise ValueError("Some weights are None or NaN.")
        return w


    # -------------------------------------------------------
    # METRICS
    # -------------------------------------------------------

    def correlation_matrix(self) -> pd.DataFrame:
        df = self._returns_df()
        return df.corr()

    def portfolio_returns(self) -> pd.Series:
        df = self._returns_df()
        w = self._weights_vector(df.columns)
        port_ret = df.dot(w)
        port_ret.name = "portfolio_return"
        return port_ret

    def portfolio_volatility(self, freq=252) -> float:
        port_ret = self.portfolio_returns()
        return float(np.sqrt(freq) * port_ret.std())

    def diversification_ratio(self, freq=252) -> float:
        df = self._returns_df()
        cov = df.cov() * freq              
        stds = df.std() * np.sqrt(freq)     

        w = self._weights_vector(df.columns)

        num = np.sum(w * stds)             
        denom = np.sqrt(w.T @ cov.values @ w)

        return float(num / denom)


    def portfolio_value(self, initial_capital=10000) -> pd.Series:
        port_ret = self.portfolio_returns()
        value = initial_capital * (1 + port_ret).cumprod()
        value.name = "portfolio_value"
        return value