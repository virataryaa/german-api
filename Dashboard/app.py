from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import comprehensive
from theme import BASE_CSS, THEME_CSS

st.set_page_config(page_title="German Coffee Consumption", layout="wide")

BLUE = "#2a78d6"
ORANGE = "#e8663a"

DATA = Path(__file__).resolve().parent.parent / "Database" / "german_coffee_tax.csv"
MONTHS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
AVG_YEARS = 5                                              # coffee years in the average, before the current one
VIEWS = ["Comprehensive View", "Crop Year Comparison"]

st.markdown(BASE_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load():
    df = pd.read_csv(DATA, parse_dates=["date"])
    df["cy_start"] = df["date"].dt.year - (df["date"].dt.month < 10)       # Oct-Sep coffee year
    df["cy"] = df["cy_start"].map(lambda y: f"{y}/{str(y + 1)[2:]}")
    df["mon"] = df["date"].dt.strftime("%b")
    return df


def comparison():
    df = load()
    piv = df.pivot_table(index="cy", columns="mon", values="bags_m").reindex(columns=MONTHS)
    years = list(piv.index)

    c1, c2, _ = st.columns([1, 1, 3])
    yb = c2.selectbox("Year", years[::-1], index=0)
    ya = c1.selectbox("Compare with", [y for y in years[::-1] if y != yb], index=0)

    # average of the five coffee years before the later selected year
    later = max(ya, yb)
    prior = [y for y in years if y < later][-AVG_YEARS:]
    avg = piv.loc[prior].mean()

    n = int(piv.loc[later].notna().sum())                 # months reported in the later year
    ytd_a, ytd_b = piv.loc[ya, MONTHS[:n]].sum(), piv.loc[yb, MONTHS[:n]].sum()
    chg = (ytd_b / ytd_a - 1) * 100
    span = f"Oct-{MONTHS[n - 1]}" if n < 12 else "Full year"

    with st.container(border=True):
        st.markdown('<div class="card-title">Crop year comparison, Oct-Sep</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="card-desc">Monthly million 60-kg bags green-equivalent. Dotted line: average of {prior[0]}-{prior[-1]}.</div>'
            f'<div class="card-desc">{span}: {yb} <b>{ytd_b:.2f}</b> M bags vs {ya} <b>{ytd_a:.2f}</b> ({chg:+.1f}%)</div>',
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        fig.add_bar(x=MONTHS, y=piv.loc[ya], name=ya, marker_color=BLUE, hovertemplate="%{x}: %{y:.3f}<extra>" + ya + "</extra>")
        fig.add_bar(x=MONTHS, y=piv.loc[yb], name=yb, marker_color=ORANGE, hovertemplate="%{x}: %{y:.3f}<extra>" + yb + "</extra>")
        fig.add_scatter(x=MONTHS, y=avg, name=f"Avg {prior[0]}-{prior[-1]}", mode="lines",
                        line=dict(color="#1a1a2e", dash="dot", width=2, shape="spline"), hovertemplate="%{x}: %{y:.3f}<extra>Avg</extra>")
        fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.05, height=460, margin=dict(l=10, r=10, t=10, b=10),
                          plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font=dict(color="#1a1a2e"),
                          legend=dict(orientation="h", y=1.08, x=0), yaxis=dict(title="M bags", rangemode="tozero", gridcolor="#eef0f6", tickformat=".2f"))
        st.plotly_chart(fig, width="stretch")


with st.container(key="mc_hero"):
    h, v = st.columns([3, 2], vertical_alignment="center")
    title = h.empty()
    with v, st.container(key="mc_page"):
        view = st.radio("View", VIEWS, horizontal=True, label_visibility="collapsed", key="view")

if view == VIEWS[0]:
    comprehensive.render(title)
else:
    title.markdown("<div class='mc-hero-t'>German Implied Coffee Consumption</div>", unsafe_allow_html=True)
    comparison()

st.caption(f"Source: Destatis GENESIS-Online table 71211-0005 (coffee tax). Bags = EUR / 2.19 per kg roasted x 1.19 green-equivalent / 60 kg. "
           f"Latest month: {load()['date'].max():%b %Y}. Soluble is taxed at EUR 4.78/kg, so the volume is an upper-bound proxy.")
st.markdown(THEME_CSS, unsafe_allow_html=True)
