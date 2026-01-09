from ui.views import *
import streamlit as st

pages = [
    st.Page(render_home, title="Home", icon=":material/home:", url_path="home", default=True),
    st.Page(render_stocks, title="Stocks", icon=":material/area_chart:", url_path="stocks"),
    st.Page(render_strategies, title="Strategies", icon=":material/chess_knight:", url_path="strategies"),
    st.Page(render_pricing, title="Pricing", icon=":material/attach_money:", url_path="pricing"),
    st.Page(render_portfolio, title="Portfolio", icon=":material/work:", url_path="portfolio")
]

pg = st.navigation(pages, position="hidden")
st.set_page_config(page_title="Financial Dashboard", layout="wide")

with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.page_link(pages[0], label="Home", icon=":material/home:", use_container_width=True)
    with col2: st.page_link(pages[1], label="Stocks", icon=":material/area_chart:", use_container_width=True)
    with col3: st.page_link(pages[2], label="Strategies", icon=":material/chess_knight:", use_container_width=True)
    with col4: st.page_link(pages[3], label="Pricing", icon=":material/attach_money:", use_container_width=True)
    with col5: st.page_link(pages[4], label="Portfolio", icon=":material/work:", use_container_width=True)
    st.divider()

pg.run()