import streamlit as st

st.set_page_config(page_title="German Coffee & Cocoa", layout="wide", initial_sidebar_state="expanded")

import importlib

import cocoa_grind
import cocoa_study
import cocoa_trade
import common
import comprehensive
import theme
import views_origins
import views_prices
import views_summary
import views_trade

# Streamlit reruns only this file; reload the helpers so a push does not leave stale modules in a running app
for _m in (theme, common, comprehensive, cocoa_grind, cocoa_study, cocoa_trade, views_summary, views_origins, views_trade, views_prices):
    importlib.reload(_m)

from common import latest_month, load_grind, load_origins, load_tax
from theme import APP_CSS, COT_CSS, FONT_CSS

st.markdown(FONT_CSS, unsafe_allow_html=True)
st.markdown(COT_CSS, unsafe_allow_html=True)
st.markdown(APP_CSS, unsafe_allow_html=True)

# page -> (sidebar controls, render); Summary stays last
PAGES = {
    "coffee": {"Consumption": (lambda: (), lambda: comprehensive.render(st.empty())),
               "Origins": (lambda: views_origins.sidebar("coffee"), views_origins.render),
               "Trade Balance": (views_trade.sidebar, views_trade.render),
               "Import Prices": (lambda: views_prices.sidebar("coffee"), views_prices.render),
               "Summary": (lambda: (), lambda: views_summary.render("coffee"))},
    "cocoa": {"Grind": (cocoa_grind.sidebar, cocoa_grind.render),
              "Origins": (lambda: views_origins.sidebar("cocoa"), views_origins.render),
              "Trade Balance": (cocoa_trade.sidebar, cocoa_trade.render),
              "Import Prices": (lambda: views_prices.sidebar("cocoa"), views_prices.render),
              "Study": (cocoa_study.sidebar, cocoa_study.render),
              "Summary": (lambda: (), lambda: views_summary.render("cocoa"))},
}

with st.sidebar:
    st.markdown("<div class='sb-title'>Germany</div><div class='sb-rule'></div>", unsafe_allow_html=True)
    comm = st.radio("Commodity", ["Coffee", "Cocoa"], horizontal=True, key="comm", label_visibility="collapsed").lower()
    page = st.radio("View", list(PAGES[comm]), key=f"nav_{comm}", label_visibility="collapsed")
    controls, render = PAGES[comm][page]
    args = controls()
    st.markdown("---")
    if comm == "coffee":
        foot = f"Coffee tax to <b>{load_tax().index.max():%b %Y}</b><br>Trade to <b>{latest_month(load_origins()):%b %Y}</b>"
    else:
        g = load_grind().iloc[-1]
        foot = f"Grind to <b>{g['crop_year']} {g['quarter']}</b><br>Trade to <b>{latest_month(load_origins('cocoa')):%b %Y}</b>"
    st.markdown(f"<div class='sb-foot'>{foot}<br>Source: Destatis</div>", unsafe_allow_html=True)

render(*args)
