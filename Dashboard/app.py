import streamlit as st

st.set_page_config(page_title="German Coffee", layout="wide", initial_sidebar_state="expanded")

import comprehensive
import views_origins
import views_prices
import views_trade
from common import load_origins, load_tax, latest_month
from theme import APP_CSS, COT_CSS, FONT_CSS

st.markdown(FONT_CSS, unsafe_allow_html=True)
st.markdown(COT_CSS, unsafe_allow_html=True)
st.markdown(APP_CSS, unsafe_allow_html=True)

PAGES = ["Consumption", "Origins", "Trade Balance", "Import Prices"]

with st.sidebar:
    st.markdown("<div class='sb-title'>German Coffee</div><div class='sb-rule'></div>", unsafe_allow_html=True)
    page = st.radio("View", PAGES, key="nav", label_visibility="collapsed")
    st.markdown("---")
    if page == "Origins":
        args = views_origins.sidebar()
    elif page == "Trade Balance":
        args = views_trade.sidebar()
    elif page == "Import Prices":
        args = views_prices.sidebar()
    else:
        args = ()
    st.markdown("---")
    st.markdown(f"<div class='sb-foot'>Coffee tax to <b>{load_tax().index.max():%b %Y}</b><br>"
                f"Trade to <b>{latest_month(load_origins()):%b %Y}</b><br>Source: Destatis GENESIS-Online</div>",
                unsafe_allow_html=True)

if page == "Consumption":
    comprehensive.render(st.empty())
elif page == "Origins":
    views_origins.render(*args)
elif page == "Trade Balance":
    views_trade.render(*args)
else:
    views_prices.render(*args)
