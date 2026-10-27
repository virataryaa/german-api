"""Summary: plain description of what each page shows and where the data comes from."""
import streamlit as st

from common import card_head, hero, latest_month, load_origins, load_tax

PAGES = [
    ("Consumption", "How much coffee Germany drinks, month by month.",
     ["Worked out from the German coffee tax: every kilo of roasted coffee sold in Germany pays €2.19, so tax money ÷ 2.19 = kilos.",
      "Shown in green-coffee terms (60 kg bags or tonnes).",
      "Chart 1: this coffee year vs last year vs the 5-year average, month by month.",
      "Chart 2: the 12-month running total since 1999.",
      "Table: every month of the last 10 coffee years, with totals and change vs the year before."]),
    ("Origins", "Where Germany's green (unroasted) coffee comes from.",
     ["Imports by country: Brazil, Vietnam, Honduras, Colombia, Ethiopia and others.",
      "Chart 1: each country's imports so far this coffee year vs the same months last year.",
      "Chart 2: the 12-month running total for the five biggest countries since 2010.",
      "Coffee shipped in from other European countries is left out, since it was grown elsewhere."]),
    ("Trade Balance", "What comes in, what goes back out, and what stays.",
     ["Germany imports green, roasted and instant coffee, and sends a large part back out to other countries.",
      "Everything is converted to green-coffee terms so it can be added up.",
      "Chart 1: last 12 months, step by step: imports, minus what was sent out, minus what was drunk = change in stock.",
      "Chart 2: coffee kept in Germany (imports minus exports) vs coffee drunk, as 12-month totals."]),
    ("Import Prices", "The average price Germany paid for its green coffee.",
     ["Price = value declared at customs ÷ weight, in US cents per pound or euros per kilo.",
      "Chart 1: average price from Arabica-growing countries vs Robusta-growing countries.",
      "Chart 2: price by country over the last 3 months, with the price a year earlier marked in red."]),
]


def render(_=None):
    hero("Summary", " · what this dashboard shows", [f"Coffee tax to {load_tax().index.max():%b %Y}",
                                                    f"Trade to {latest_month(load_origins()):%b %Y}"])
    st.markdown("<div class='card-desc' style='font-size:13px;margin:0 0 14px'>Four pages, picked in the sidebar. "
                "All numbers come from Destatis, Germany's official statistics office, and update monthly. "
                "A coffee year runs October to September.</div>", unsafe_allow_html=True)
    for i in range(0, len(PAGES), 2):
        cols = st.columns(2, gap="medium")
        for col, (name, what, points) in zip(cols, PAGES[i:i + 2]):
            with col, st.container(border=True):
                card_head(name, what)
                st.markdown("<ul style='margin:4px 0 2px 18px;padding:0;font-size:13px;line-height:1.6;color:#1a1a2e'>"
                            + "".join(f"<li>{p}</li>" for p in points) + "</ul>", unsafe_allow_html=True)
    with st.container(border=True):
        card_head("Good to know")
        st.markdown("<ul style='margin:4px 0 2px 18px;padding:0;font-size:13px;line-height:1.6;color:#1a1a2e'>"
                    "<li>Trade figures come out about a month after the tax figures.</li>"
                    "<li>The consumption number is an estimate: instant coffee pays a higher tax rate, so it reads slightly high.</li>"
                    "<li>Customs prices trail market prices by a few months, because coffee is bought well before it arrives.</li>"
                    "<li>Sources: Destatis tables 71211-0005 (coffee tax), 51000-0014 and 51000-0018 (foreign trade).</li></ul>",
                    unsafe_allow_html=True)
