import streamlit as st
import yfinance as yf
import pandas as pd


@st.cache_data(ttl=3600)
def fetch_prices(tickers: tuple, periodo_dias: int = 504) -> pd.DataFrame:
    periodo_map = {126: "6mo", 252: "1y", 504: "2y", 756: "3y"}
    periodo = periodo_map.get(periodo_dias, "2y")
    try:
        df = yf.download(list(tickers), period=periodo, auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df = df["Close"]
        else:
            df.columns = list(tickers)
        return df.dropna(how="all")
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return pd.DataFrame()


def validar_ticker(ticker: str) -> bool:
    try:
        info = yf.Ticker(ticker).fast_info
        return hasattr(info, "last_price") and info.last_price is not None
    except Exception:
        return False
