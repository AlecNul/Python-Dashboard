import streamlit as st

from classes.Asset import Asset
from classes.BuyHold import BuyHold
from classes.Momentum import Momentum

from load_data.news_scraper import get_latest_news
import pandas as pd
import datetime

def render_home():
    st.title("Home")
    st.write("Welcome to the Financial Dashboard.")

    # Displaying last scraped news
    latest_news = get_latest_news()

    for index, row in latest_news.iterrows():
                with st.container():
                    c1, c2 = st.columns([1, 5])
                    
                    with c1:
                        # Date
                        st.caption(f"Time : {row['date']}")
                    with c2:
                        # Title and link
                        st.markdown(f"**[{row['title']}]({row['link']})**")
                        # Tickers
                        if (pd.notna(row['tickers']) and row['tickers'] != "MARKET"):
                            badges = " ".join(row['tickers'])
                            st.markdown(f"{badges}")
                st.divider()

def render_stocks():
    st.title("Stocks Analysis")
    st.write("Graphs and metrics here.")

# Choosing the ticker
    ticker_input = st.text_input(
        label="Type a ticker",
        placeholder="Ex: NVDA, TSLA, BTC-USD..."
    ).upper()

# Showing candle graph
    if ticker_input:
        my_asset = Asset(ticker_input)

        if my_asset.history.empty:
            st.error(f"No data found for this ticker : '{ticker_input}'.")
        else:
            graph_type = st.radio("Graph Type", ["Candlestick", "Line Price"], horizontal=True)
            
            opt_col1, opt_col2 = st.columns(2)
            show_mean = opt_col1.checkbox("Add Rolling Mean (20d)")
            show_std = opt_col2.checkbox("Add Rolling Volatility (20d)")

            # Handle graph type
            if graph_type == "Candlestick":
                fig = my_asset.candle_graph()
            else:
                fig = my_asset.price_graph()
            # Handle rolling mean / std to add
            if show_mean:
                fig = my_asset.add_rolling_mean(fig, w=20)
            if show_std:
                fig = my_asset.add_rolling_std(fig, w=20)

            st.plotly_chart(fig, use_container_width=True)

def render_strategies():
    
    st.title("Backtest")
    st.write("Choose a ticker to try a strategy")

    # Choosing the ticker
    ticker_input = st.text_input(
        label="Type a ticker",
        placeholder="Ex: NVDA, TSLA, BTC-USD..."
    ).upper()

    if ticker_input:
        my_asset = Asset(ticker_input)

        if my_asset.history.empty:
            st.error(f"No data found for this ticker : '{ticker_input}'.")
        else:

            # Date inputs (it has no timezone ! so we need to add one manually)
            c1, c2 = st.columns(2)
            with c1:
                start_date_input = st.date_input(
                label="Type the start date"
                )
            with c2:
                end_date_input = st.date_input(
                label="Type the end date"
                )

            # Handling the timezone issue, by using the same a yfinance
            asset_tz = my_asset.prices.index.tz

            start_ts = pd.Timestamp(start_date_input)
            end_ts = pd.Timestamp(end_date_input)

            if asset_tz is not None:
                start_date = start_ts.tz_localize(asset_tz)
                end_date = end_ts.tz_localize(asset_tz)
            else:
                start_date = start_ts
                end_date = end_ts
            
            # Choose the strategy
            opt_col1, opt_col2 = st.columns(2)
            is_buyhold = opt_col1.checkbox("Test Buy and Hold Strategy")
            is_momentum = opt_col2.checkbox("Test Momentum Strategy")

            if is_buyhold:
                my_strat = BuyHold(my_asset,start_date,end_date)
            elif is_momentum:
                my_strat = Momentum(my_asset,start_date,end_date)

            st.divider()
            st.subheader("Capital over time")

            fig = my_strat.capital_graph()
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.subheader("Key Metrics (Annualized)")

            metrics_data = {
                    "Metric": [
                        "Annualized Volatility",
                        "Sharpe Ratio", 
                        "Sortino Ratio",
                        "Max Drawdown",
                        "VaR (95%)",
                        "Expected Shortfall (95%)"
                    ],
                    "Value": [
                        f"{my_strat.annualized_volatility():.2%}", 
                        f"{my_strat.sharpe():.2f}",
                        f"{my_strat.sortino():.2f}",
                        f"{my_strat.max_drawdown():.2%}",
                        f"{my_strat.historical_VaR(0.95):.2%}",
                        f"{my_strat.historical_ES(0.95):.2%}"
                    ]
                }

def render_pricing():
    st.title("Option Pricing")
    st.write("WIP : Need to use C++ files.")