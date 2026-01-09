# Financial Analysis & Backtesting Dashboard

🔗 **Live application:** http://13.48.203.189:8501  

**Author:** Alec REYNEN and Thibault PELOU  
**Stack:** Python | Streamlit | Plotly | Pandas  

---

## Overview

This project is a comprehensive **Financial Analysis & Backtesting Dashboard** deployed on **AWS (EC2)**.  
It allows users to visualize market data, analyze asset risk profiles, and backtest various investment strategies through an interactive web interface.

---

## Key Features

* **Market Data:**  
  Real-time retrieval of OHLCV data via Yahoo Finance (`yfinance`) and financial news via Finviz scraping.

* **Interactive Visualization:**  
  Candlestick charts and dynamic plots powered by Plotly and Streamlit.

* **Risk Metrics:**  
  * Value at Risk (VaR) & Expected Shortfall (ES)  
  * Sharpe & Sortino Ratios  
  * Maximum Drawdown  
  * Annualized Volatility  

* **Backtesting Engine:**  
  An Object-Oriented engine to simulate investment strategies (e.g. Buy & Hold) and compare their performance against benchmarks.

---

## Technical Architecture

The project follows a modular **Object-Oriented Programming (OOP)** architecture to ensure scalability, readability, and maintainability.

### Data Sources
* **Yahoo Finance (`yfinance`)**: Historical price data and risk-free rates.
* **Web Scraping (Finviz)**: Financial news and selected fundamental indicators.

### Code Structure

The application is divided into logical modules inside the `src/` directory:

* `classes/` – Core business logic  
  * **`Asset` class:** Data loading, preprocessing, and risk metric computation  
  * **`Strategy` class:** Base class for backtesting strategies (Buy & Hold, Moving Averages, etc.)

* `ui/` – Streamlit user interface components (tabs, sidebar, charts)

* `load_data/` – Utility scripts for fetching and updating external data

---

## Deployment (AWS)

The application is deployed on an **AWS EC2 instance** and is accessible through a public IP address.

* **Web framework:** Streamlit  
* **Server:** Amazon EC2 (Linux)  
* **Automation:**  
  A daily cron job generates an automated report every day at **20:00**, independently from the Streamlit interface.

⚠️ *The application is hosted on a student AWS account and may not be permanently available.*

---

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run src/app.py
