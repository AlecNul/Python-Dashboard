import streamlit as st
from classes.Asset import Asset
from load_data.news_scraper import get_latest_news
import pandas as pd

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
            st.divider()
            st.subheader("Key Metrics (Annualized)")

            last_price = my_asset.prices.iloc[-1]
            prev_price = my_asset.prices.iloc[-2]
            daily_return = (last_price - prev_price) / prev_price
            volatility = my_asset.rolling_std(window=252).iloc[-1]*(252**0.5)
            mean = my_asset.rolling_mean(window=252).iloc[-1]*(252**0.5)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Last Price", f"{last_price:.2f} $", delta=f"{daily_return:.2%}")
            c2.metric("Volatility", f"{volatility:.2%}")
            c3.metric("Mean", f"{mean:.2%}")

def render_strategies():
    st.title("Backtest")
    st.write("Run backtests here.")

def render_pricing():
    st.title("Option Pricing")
    st.write("WIP : Need to use C++ files.")