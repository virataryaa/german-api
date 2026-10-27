"""Summary: plain description of what each page shows and where the data comes from."""
import streamlit as st

from common import card_head, hero, latest_month, load_origins, load_tax

PAGES = [
    ("Consumption", "How much coffee Germany drinks each month.",
     ["Germany puts a tax on coffee: €2.19 for every kilo sold. So tax paid ÷ 2.19 tells us how many kilos were sold.",
      "Shown in 60 kg bags or tonnes of raw coffee.",
      "Chart 1: this year, last year and the 5-year average, month by month.",
      "Chart 2: the total for the last 12 months, going back to 1999.",
      "Table: each month of the last 10 years, with totals."]),
    ("Origins", "Which countries Germany buys raw coffee from.",
     ["For example Brazil, Vietnam, Honduras, Colombia, Ethiopia.",
      "Chart 1: how much came from each country this year, next to the same months last year.",
      "Chart 2: the last-12-months total for the 5 biggest countries.",
      "Coffee that came through other European countries is not counted here."]),
    ("Trade Balance", "Coffee coming in, coffee going out, and what is left.",
     ["Germany buys raw, roasted and instant coffee, and sells a lot of it on to other countries.",
      "All of it is turned into raw-coffee weight so it can be added up.",
      "Chart 1: last 12 months. Coffee in, minus coffee out, minus coffee drunk = what is left over.",
      "Chart 2: coffee kept in Germany next to coffee drunk, last-12-months totals."]),
    ("Import Prices", "What Germany paid for raw coffee.",
     ["Price = money paid ÷ weight. Shown in US cents per pound or euros per kilo.",
      "Chart 1: price of Arabica coffee next to Robusta coffee.",
      "Chart 2: price from each country now. The red mark is the price one year ago."]),
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
