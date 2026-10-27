"""Summary: plain description of what each page shows and where the data comes from."""
import streamlit as st

from common import card_head, hero, latest_month, load_origins, load_tax

PAGES = [
    ("Consumption", "How much coffee Germany drinks each month.",
     ["Germany puts a tax on coffee: €2.19 for every kilo sold. So tax paid ÷ 2.19 tells us how many kilos were sold.",
      "Shown in bags or tonnes of raw coffee.",
      "Charts: each month next to past years, the running total for the year, and the last-12-months total.",
      "Table and bars: each month of past years, the full-year totals, and this year so far next to last year."]),
    ("Origins", "Which countries Germany buys raw coffee from.",
     ["For example Brazil, Vietnam, Honduras, Colombia, Ethiopia.",
      "Charts: each month by country, this year next to last year, each country's share by year, and the last-12-months total.",
      "Pick one country to see its months and running total next to past years.",
      "Table: each country by year."]),
    ("Trade Balance", "Coffee coming in, coffee going out, and what is left.",
     ["Germany buys raw, roasted and instant coffee, and sells a lot of it on to other countries.",
      "All of it is turned into raw-coffee weight so it can be added up.",
      "Charts: coffee in minus coffee out minus coffee drunk, coffee kept next to coffee drunk, in and out for each kind, "
      "what is left over each year, and where the raw coffee is sold to.",
      "Table: all of it by year."]),
    ("Import Prices", "What Germany paid for raw coffee.",
     ["Price = money paid ÷ weight. Shown in US cents per pound or euros per kilo.",
      "Charts: Arabica next to Robusta, the price from countries you pick, and each country's price now next to one year ago.",
      "Table: price and amount bought for each country."]),
]

NOTES = [
    "Trade numbers come out about one month after the tax numbers.",
    "The drinking number is an estimate. Instant coffee pays more tax, so the number comes out a little high.",
    "Prices here are a few months behind market prices, because coffee is bought long before it arrives.",
    "Data: Destatis (German statistics office), tables 71211-0005, 51000-0014 and 51000-0018.",
]
UL = "<ul style='margin:4px 0 2px 18px;padding:0;font-size:13px;line-height:1.6;color:#1a1a2e'>{}</ul>"


def render(_=None):
    hero("Summary", " · what is in this dashboard", [f"Tax data to {load_tax().index.max():%b %Y}",
                                                     f"Trade data to {latest_month(load_origins()):%b %Y}"])
    st.markdown("<div class='card-desc' style='font-size:13px;margin:0 0 14px'>Four pages. Pick one in the menu on the left. "
                "New numbers come in every month. A coffee year runs from October to September.</div>", unsafe_allow_html=True)
    for i in range(0, len(PAGES), 2):
        for col, (name, what, points) in zip(st.columns(2, gap="medium"), PAGES[i:i + 2]):
            with col, st.container(key=f"sum_{name.replace(' ', '_').lower()}"):
                card_head(name, what)
                st.markdown(UL.format("".join(f"<li>{p}</li>" for p in points)), unsafe_allow_html=True)
    with st.container(key="sum_note"):
        card_head("Note")
        st.markdown(UL.format("".join(f"<li>{p}</li>" for p in NOTES)), unsafe_allow_html=True)
