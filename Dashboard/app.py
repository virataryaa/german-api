from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="German Coffee Consumption", layout="wide")

NAVY = "#0a2463"
BLUE = "#2a78d6"
ORANGE = "#e8663a"
GREY = "#8a94a8"

DATA = Path(__file__).resolve().parent.parent / "Database" / "german_coffee_tax.csv"
MONTHS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]
AVG_YEARS = 5                                              # coffee years in the average, before the current one

st.markdown(
    """
<style>
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main { background: #fafafa !important; }
[data-testid="stHeader"] { background: #fafafa !important; }
h1, h2, h3, h4, h5, h6 { color: #0a2463 !important; }
body, .main { color: #1a1a2e; }
.block-container { padding-top: 2.6rem; padding-bottom: 1rem; }
.card-desc { color: #5a6688; font-size: 0.82rem; margin-top: -6px; margin-bottom: 10px; }
.card-title { color: #0a2463; font-weight: 700; font-size: 1rem; margin-bottom: 2px; }
.kpi { color: #5a6688; font-size: 0.85rem; margin-bottom: 4px; }
.kpi b { color: #1a1a2e; }
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {
    background: #ffffff; border: 1px solid #e3e7f0 !important; border-radius: 12px;
    box-shadow: 0 1px 3px rgba(10,36,99,0.06); }
.dtab { width: auto; border-collapse: collapse; font-size: 11px; line-height: 1.1; background: #ffffff; }
.dtab th { text-align: center; padding: 2px 6px; font-weight: 600; white-space: nowrap; background: #0a2463; color: #ffffff; }
.dtab td { text-align: right; padding: 1px 6px; border-bottom: 1px solid #eef0f6; white-space: nowrap; color: #1a1a2e; }
.dtab td.dt { text-align: left; font-weight: 700; background: #f0f2f8; }
.dtab td.b { font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data(ttl=3600)
def load():
    df = pd.read_csv(DATA, parse_dates=["date"])
    df["cy_start"] = df["date"].dt.year - (df["date"].dt.month < 10)       # Oct-Sep coffee year
    df["cy"] = df["cy_start"].map(lambda y: f"{y}/{str(y + 1)[2:]}")
    df["mon"] = df["date"].dt.strftime("%b")
    return df


df = load()
piv = df.pivot_table(index="cy", columns="mon", values="bags_m").reindex(columns=MONTHS)
years = list(piv.index)
cur = years[-1]

st.markdown("## German Implied Coffee Consumption")
st.markdown(
    '<div class="card-desc">Destatis coffee tax receipts (table 71211-0005) / EUR 2.19 per kg roasted x 1.19 green-equivalent / 60 kg. '
    f'Latest month: {df["date"].max():%b %Y}.</div>',
    unsafe_allow_html=True,
)

c1, c2 = st.columns(2)
yb = c2.selectbox("Year", years[::-1], index=0)
ya = c1.selectbox("Compare with", [y for y in years[::-1] if y != yb], index=0)

# average of the five coffee years before the later selected year
later = max(ya, yb)
prior = [y for y in years if y < later][-AVG_YEARS:]
avg = piv.loc[prior].mean()

n = int(piv.loc[later].notna().sum())                     # months reported in the later year
ytd_a, ytd_b = piv.loc[ya, MONTHS[:n]].sum(), piv.loc[yb, MONTHS[:n]].sum()
chg = (ytd_b / ytd_a - 1) * 100
span = f"Oct-{MONTHS[n - 1]}" if n < 12 else "Full year"

with st.container(border=True):
    st.markdown('<div class="card-title">Crop year comparison, Oct-Sep</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="card-desc">Monthly million 60-kg bags green-equivalent. Dotted line: average of {prior[0]}-{prior[-1]}.</div>'
        f'<div class="kpi">{span}: {yb} <b>{ytd_b:.2f}</b> M bags vs {ya} <b>{ytd_a:.2f}</b> ({chg:+.1f}%)</div>',
        unsafe_allow_html=True,
    )
    fig = go.Figure()
    fig.add_bar(x=MONTHS, y=piv.loc[ya], name=ya, marker_color=BLUE, hovertemplate="%{x}: %{y:.3f}<extra>" + ya + "</extra>")
    fig.add_bar(x=MONTHS, y=piv.loc[yb], name=yb, marker_color=ORANGE, hovertemplate="%{x}: %{y:.3f}<extra>" + yb + "</extra>")
    fig.add_scatter(x=MONTHS, y=avg, name=f"Avg {prior[0]}-{prior[-1]}", mode="lines", line=dict(color="#1a1a2e", dash="dot", width=2, shape="spline"),
                    hovertemplate="%{x}: %{y:.3f}<extra>Avg</extra>")
    fig.update_layout(barmode="group", bargap=0.25, bargroupgap=0.05, height=430, margin=dict(l=10, r=10, t=10, b=10),
                      plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font=dict(color="#1a1a2e"),
                      legend=dict(orientation="h", y=1.08, x=0), yaxis=dict(title="M bags", rangemode="tozero", gridcolor="#eef0f6", tickformat=".2f"))
    st.plotly_chart(fig, width="stretch")

with st.container(border=True):
    st.markdown('<div class="card-title">Coffee year totals</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-desc">Million bags by month, last 8 coffee years. Total is shown only for complete years.</div>', unsafe_allow_html=True)
    head = "".join(f"<th>{m}</th>" for m in ["Year"] + MONTHS + ["Total", "YoY"])
    body, prev = "", None
    for y in years[-9:]:
        r = piv.loc[y]
        tot = r.sum() if r.notna().all() else None
        yoy = f"{(tot / prev - 1) * 100:+.1f}%" if tot and prev else ""
        cells = "".join(f"<td>{v:.3f}</td>" if pd.notna(v) else "<td></td>" for v in r)
        if y != years[-9]:
            body += f'<tr><td class="dt">{y}</td>{cells}<td class="b">{f"{tot:.2f}" if tot else ""}</td><td>{yoy}</td></tr>'
        prev = tot
    st.markdown(f'<table class="dtab"><tr>{head}</tr>{body}</table>', unsafe_allow_html=True)

st.caption("Source: Destatis GENESIS-Online. Receipts include soluble at a higher rate (EUR 4.78/kg), so the volume is an upper-bound proxy.")
