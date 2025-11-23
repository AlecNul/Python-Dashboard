from classes.Asset import Asset
import streamlit as st

Asset1 = Asset("AAPL")

def main(Asset1:Asset):
    st.title("Beautiful Python Dashboard")
    ticker = st.sidebar.text_input("Ticker", value=Asset1.ticker_symbol)
    duration = st.sidebar.selectbox(
        "Period",
        options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        index=6
    )

    # Display a checkbox with the label 'Show/Hide'
    if st.checkbox("Candle Graph"):
    # Show this text only when the checkbox is checked
        fig = Asset1.candle_graph(duration)

        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Erreur lors de la récupération des données.")

main(Asset1)

# st.dataframe(data)

# st.title(f"Historique des prix de {Asset1.ticker_symbol}")