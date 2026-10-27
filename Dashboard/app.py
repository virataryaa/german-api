import streamlit as st

st.set_page_config(page_title="German Coffee", layout="wide", initial_sidebar_state="expanded")

import importlib

import common
import theme
import views_consumption
import views_origins
import views_prices
import views_trade

# Streamlit reruns only this file; reload the helpers so a push does not leave stale modules in a running app
for _m in (theme, common, views_consumption, views_origins, views_trade, views_prices):
    importlib.reload(_m)

from common import UNITS, latest_month, load_origins, load_tax
from theme import APP_CSS, COT_CSS, FONT_CSS

st.markdown(FONT_CSS, unsafe_allow_html=True)
st.markdown(COT_CSS, unsafe_allow_html=True)
st.markdown(APP_CSS, unsafe_allow_html=True)

PAGES = {"Consumption": views_consumption, "Origins": views_origins, "Trade Balance": views_trade, "Import Prices": views_prices}

with st.sidebar:
    st.markdown("<div class='sb-title'>German Coffee</div><div class='sb-rule'></div>", unsafe_allow_html=True)
    page = st.radio("View", list(PAGES), key="nav", label_visibility="collapsed")
    st.markdown("---")
    if page == "Import Prices":
        arg = st.radio("Price unit", list(views_prices.CCY), horizontal=True, key="ccy")
    else:
        arg = st.radio("Unit", list(UNITS), index=1, horizontal=True, key="unit")
    st.markdown(f"<div class='sb-foot'>Coffee tax to <b>{load_tax().index.max():%b %Y}</b><br>"
                f"Trade to <b>{latest_month(load_origins()):%b %Y}</b><br>Source: Destatis GENESIS-Online</div>",
                unsafe_allow_html=True)

PAGES[page].render(arg)
