"""Summary: one small table of what each page shows."""
import streamlit as st

from common import hero, latest_month, load_origins, load_tax

ROWS = [
    ("Consumption", "How much coffee Germany drinks each month", "Coffee tax ÷ €2.19 per kilo"),
    ("Origins", "Which countries Germany buys raw coffee from", "Customs, by country"),
    ("Trade Balance", "Coffee in, coffee out, and what is left", "Customs + coffee tax"),
    ("Import Prices", "What Germany paid for raw coffee", "Money paid ÷ weight"),
]
NOTE = ("Source: Destatis. New numbers every month; trade comes one month after tax. "
        "A coffee year runs October to September. Consumption is an estimate and prices trail the market by a few months.")


def render(_=None):
    hero("Summary", "", [f"Tax data to {load_tax().index.max():%b %Y}", f"Trade data to {latest_month(load_origins()):%b %Y}"])
    body = "".join(f"<tr><td class='n'>{p}</td><td>{w}</td><td class='m'>{d}</td></tr>" for p, w, d in ROWS)
    st.markdown(f"<table class='sum'><tr><th>Page</th><th>What it shows</th><th>From</th></tr>{body}</table>"
                f"<div class='sum-note'>{NOTE}</div>", unsafe_allow_html=True)
