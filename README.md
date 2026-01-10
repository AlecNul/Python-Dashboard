# Financial Analysis & Backtesting Dashboard

**Author:** Alec REYNEN and Thibault PELOU
**Stack:** Python | Streamlit | Plotly | Pandas

## Overview

This project is a comprehensive Financial Dashboard, which will be hosted on a AWS (EC2), it allows users to visualize market data, analyze asset risk profiles, and backtest various investment strategies.

### Key Features
* **Market Data:** Real-time retrieval of OHLCV data via Yahoo Finance (`yfinance`) and news via Finviz scraping.
* **Interactive Visualization:** Candle graph.
* **Risk Metrics:**
    * Value at Risk (VaR) & Expected Shortfall (ES)
    * Sharpe & Sortino Ratios
    * Maximum Drawdown and Annualized Volatility
* **Backtesting Engine:** An Object-Oriented engine to simulate strategies (e.g., Buy and Hold) and compare their performance against benchmarks.

---

## Technical Architecture

The project follows a modular **Object-Oriented Programming (OOP)** structure to ensure scalability and maintainability.

### Data Sources
* **yfinance:** For historical price data and treasury rates (Risk-Free Rate).
* **Web Scraping (Finviz):** For fundamental ratios and news sentiment.

### Code Structure
The application is divided into logical modules within the `src/` directory:

* `classes/`: Contains the core logic.
    * **`Asset` class:** Handles data loading, slicing, and risk metric calculations.
    * **`Strategy` class:** Parent class for backtesting logic (BuyHold, MovingAverages, etc.).
* `ui/`: Manages the Streamlit components (Tabs, Sidebar, Charts).
* `data_loader/`: Utility scripts for fetching and caching external data.

