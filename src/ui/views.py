import streamlit as st

from classes.Asset import Asset
from classes.BuyHold import BuyHold
from classes.Momentum import Momentum

from load_data.news_scraper import get_latest_news
import pandas as pd
import datetime
import plotly.graph_objects as go

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
    st.write("Analyze asset price and risk metrics (EVT).")

    # Input
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ticker_input = st.text_input(
            label="Ticker Symbol",
            value="SPY",
            placeholder="Ex: NVDA, TSLA, BTC-USD..."
        ).upper()
    
    with col2:
        # Let's choose 1y ago as a default start
        default_start = datetime.date.today() - datetime.timedelta(days=365)
        start_date = st.date_input("Start Date", value=default_start)
        
    with col3:
        end_date = st.date_input("End Date", value=datetime.date.today())

    my_asset = Asset(ticker_input, start_date=start_date, end_date=end_date)

    if my_asset.history.empty:
        st.error(f"No data found for '{ticker_input}' on these dates.")
        return

    # Graphs
    graph_type = st.radio("Graph Type", ["Candlestick", "Line Price"], horizontal=True)
        
    opt_col1, opt_col2 = st.columns(2)
    show_mean = opt_col1.checkbox("Add Rolling Mean")
    show_std = opt_col2.checkbox("Add Rolling Volatility")

    if graph_type == "Candlestick":
        fig = my_asset.candle_graph()
    else:
        fig = my_asset.price_graph()
        
    if show_mean:
        window_mean = opt_col1.number_input("Choose mean window", value=20, min_value=2)
        fig = my_asset.add_rolling_mean(fig, w=window_mean)
    if show_std:
        window_std = opt_col2.number_input("Choose volatility window", value=20, min_value=2)
        fig = my_asset.add_rolling_std(fig, w=window_std)

    st.plotly_chart(fig, use_container_width=True)

    # EVT
    st.divider()
    st.subheader("Extreme Value Analysis (Hill Plot)")

    hill_series = my_asset.get_hill_estimator()

    if hill_series.empty:
        st.warning("Not enough loss data to compute the Hill estimator.")
    else:
        # Graph
        fig_hill = go.Figure()
        
        fig_hill.add_trace(go.Scatter(
            x=hill_series.index,
            y=hill_series.values,
            mode='lines',
            name='Hill Estimator',
            line=dict(color='#FFA500') 
        ))
        fig_hill.update_layout(
            title=f"Hill Plot: {my_asset.ticker_symbol}",
            xaxis_title="Number of Extremes (k)",
            yaxis_title="Tail Index Estimation (ksi)",
            template="plotly_dark",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_hill, use_container_width=True)

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
            
            data_in_range = my_asset.prices.loc[start_date:end_date]
            
            if data_in_range.empty:
                st.error(f"No data found between {start_date.date()} and {end_date.date()}. Adjust the dates")
                return

            # Choose the strategies to compare
            opt_col1, opt_col2 = st.columns(2)
            active_strategies = []

            # BuyHold
            if opt_col1.checkbox("Test Buy and Hold Strategy"):
                buyhold_strat = BuyHold(my_asset, start_date, end_date)
                active_strategies.append(("Buy and Hold", buyhold_strat))

            # Momentum
            if opt_col2.checkbox("Test Momentum Strategy"):
                my_window = opt_col2.number_input(
                    "Mobile Mean (Days)", 
                    min_value=1, 
                    max_value=200, 
                    value=20,
                    step=1
                )
                momentum_strat = Momentum(my_asset, start_date, end_date)
                momentum_strat.define_positions(w=my_window) 
                active_strategies.append((f"Momentum (w={my_window} days)", momentum_strat))

            if not active_strategies:
                st.info("Please select at least one strategy to see the results.")
            else:
                st.subheader("Capital over time")

                # Adding the graphs we want to compare
                fig = go.Figure()
                
                for name, strat in active_strategies:
                    equity_curve = strat.get_equity_curve()
                    
                    fig.add_trace(go.Scatter(
                        x=equity_curve.index,
                        y=equity_curve,
                        mode='lines',
                        name=name, 
                    ))

                fig.add_hline(y=active_strategies[0][1].capital, line_dash="dash", line_color="gray", annotation_text="Initial Capital")
                
                fig.update_layout(
                    title="Equity Curve Comparison",
                    yaxis_title="Capital Value ($)",
                    xaxis_title="Date",
                    template="plotly_dark",
                    hovermode="x unified"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Metrics
                st.divider()
                st.subheader("Metrics Comparison")

                metrics_list = []
                for name, strat in active_strategies:
                    pnl_value, pnl_pct = strat.pnl()
                    _, mdd = strat.drawdown()
                    metrics_list.append({
                        "Strategy": name,
                        "PnL": f"{pnl_value:.2f} ({pnl_pct:.2%})",
                        "Annualized Volatility": f"{strat.annualized_volatility():.2%}",
                        "Sharpe Ratio": f"{strat.sharpe():.2f}",
                        "Sortino Ratio": f"{strat.sortino():.2f}",
                        "Max Drawdown": f"{mdd:.2%}",
                        "VaR (95%)": f"{strat.historical_VaR(0.95):.2%}",
                        "Exp. Shortfall": f"{strat.historical_ES(0.95):.2%}"
                    })

                st.dataframe(pd.DataFrame(metrics_list).set_index("Strategy"))

def render_pricing():
    st.title("Option Pricing")
    st.write("WIP : We could try to use Cpp files from Cpp pricing project.")

#############################
# QUANT B - PORTFOLIO
#############################

from classes.portfolio import Portfolio

def render_portfolio():
    st.title("Portfolio (Quant B)")

    # Simple demo portfolio
    p = Portfolio("Demo Portfolio")
    p.add_asset("AAPL", 0.5)
    p.add_asset("MSFT", 0.5)

    if not p.check_weights():
        st.error("Portfolio weights must sum to 1.")
        return

    st.subheader("Portfolio Volatility")
    st.write(f"{p.portfolio_volatility():.2%}")

    st.subheader("Diversification Ratio")
    st.write(f"{p.diversification_ratio():.2f}")

    st.subheader("Correlation Matrix")
    st.dataframe(p.correlation_matrix())

    st.subheader("Portfolio Value")
    st.line_chart(p.portfolio_value())
