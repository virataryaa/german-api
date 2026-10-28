"""Summary: one small table of what each page shows."""
import streamlit as st

from common import hero, latest_month, load_grind, load_origins, load_tax

ROWS = {
    "coffee": [
        ("Consumption", "How much coffee Germany drinks each month", "Coffee tax ÷ €2.19 per kilo"),
        ("Origins", "Which countries Germany buys raw coffee from", "Customs, by country"),
        ("Trade Balance", "Coffee in, coffee out, and what is left", "Customs + coffee tax"),
        ("Import Prices", "What Germany paid for raw coffee", "Money paid ÷ weight; mainly Arabica, mainly Robusta and Brazil"),
    ],
    "cocoa": [
        ("Grind", "How many cocoa beans German factories process each quarter", "German cocoa industry (BDSI)"),
        ("Origins", "Which countries Germany buys cocoa beans from", "Customs, by country"),
        ("Trade Balance", "Beans, paste, butter, powder and chocolate in and out", "Customs, turned into bean weight"),
        ("Import Prices", "What Germany paid for cocoa beans", "Money paid ÷ weight; West Africa, Latin America, other"),
    ],
}
NOTE = {
    "coffee": ("Source: Destatis. New numbers every month; trade comes one month after tax. "
               "A coffee year runs October to September. Consumption is an estimate and prices trail the market by a few months."),
    "cocoa": ("Source: Destatis and BDSI. Trade is monthly, grind is quarterly. A cocoa year runs October to September. "
              "Chocolate is counted at about 40% beans, so its bean weight is an estimate; prices trail the market by a few months."),
}


def render(comm="coffee"):
    if comm == "coffee":
        chips = [f"Tax data to {load_tax().index.max():%b %Y}", f"Trade data to {latest_month(load_origins()):%b %Y}"]
    else:
        g = load_grind().iloc[-1]
        chips = [f"Grind to {g['crop_year']} {g['quarter']}", f"Trade data to {latest_month(load_origins('cocoa')):%b %Y}"]
    hero("Summary", f" · {comm}", chips)
    body = "".join(f"<tr><td class='n'>{p}</td><td>{w}</td><td class='m'>{d}</td></tr>" for p, w, d in ROWS[comm])
    st.markdown(f"<table class='sum'><tr><th>Page</th><th>What it shows</th><th>From</th></tr>{body}</table>"
                f"<div class='sum-note'>{NOTE[comm]}</div>", unsafe_allow_html=True)
