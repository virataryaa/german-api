"""Shared bits for the trade pages: data loaders, coffee-year helpers, plot base (COT_ALL type scale), KPI tiles, tables."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DB = Path(__file__).resolve().parent.parent / "Database"

NAVY, TEAL, GREEN, RED, AMBER, GREY = "#0a2463", "#1f8a9c", "#1f9d6f", "#c94a4a", "#c98a1f", "#8a94a8"
WINE, ORANGE, PURPLE, SKY = "#7b1e3a", "#e8770a", "#7a4fa0", "#6b9bd2"
INK, AXIS, GRID = "#1a1a2e", "#4a5578", "rgba(10,36,99,0.08)"
SERIES = [NAVY, AMBER, TEAL, RED, GREEN, PURPLE, SKY, WINE, "#9a6b3f", "#5f7a3a"]
OTHER_C = "#c3cbe0"
H = 320                  # one compact chart height for every page
MONTHS = ["Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"]   # coffee year Oct-Sep

# ICO green-bean-equivalent factors
GBE = {"Green": 1.0, "Green decaf": 1.0, "Roasted": 1.19, "Roasted decaf": 1.19, "Soluble": 2.6}
# ICCO bean-equivalent factors; chocolate at ~40% cocoa content is an estimate (its HS codes mix many recipes)
CBE = {"Beans": 1.0, "Paste": 1.25, "Butter": 1.33, "Powder": 1.18, "Chocolate": 0.4}
BAG_T = 0.06
LB_PER_T = 2204.62

NAMES = {"Viet-Nam": "Vietnam", "Tanzania, United Republic of": "Tanzania", "Belgium (since 1999)": "Belgium",
         "Congo, Democratic Republic of": "DR Congo", "Lao People's Democratic Republic": "Laos",
         "Bolivia, Plurinational State of": "Bolivia", "Venezuela, Bolivarian Republic of": "Venezuela",
         "Korea, Republic of": "South Korea", "United States of America": "USA", "United Kingdom": "UK",
         "Netherlands": "Netherlands", "Côte d'Ivoire": "Ivory Coast", "Cote d'Ivoire": "Ivory Coast",
         "Russian Federation": "Russia", "Switzerland (incl. Büsingen)": "Switzerland",
         "Dominican Republic": "Dominican Rep."}
EUROPE = {"Belgium", "Netherlands", "Spain", "Italy", "France", "Austria", "Poland", "Switzerland", "UK", "Denmark",
          "Sweden", "Czechia", "Portugal", "Luxembourg", "Slovenia", "Slovakia", "Hungary", "Greece", "Ireland",
          "Finland", "Croatia", "Romania", "Bulgaria", "Lithuania", "Latvia", "Estonia", "Norway", "Malta", "Cyprus"}
ROBUSTA = {"Vietnam", "Uganda", "Indonesia", "India", "Ivory Coast", "Laos", "Cameroon", "Thailand", "DR Congo",
           "Togo", "Guinea", "Madagascar", "Malaysia"}


def clean_name(s):
    s = str(s).strip()
    return NAMES.get(s, s)


# ── Data ──────────────────────────────────────────────────────────────────────
def _cy(d: pd.Series):
    y = d.dt.year - (d.dt.month < 10)
    return y.map(lambda v: f"{v % 100:02d}/{(v + 1) % 100:02d}"), (d.dt.month - 10) % 12 + 1


@st.cache_data(ttl=3600)
def load_tax() -> pd.DataFrame:
    d = pd.read_csv(DB / "german_coffee_tax.csv", parse_dates=["date"])
    d["cons_t"] = d["bags_m"] * 1e6 * BAG_T                     # green-equivalent tonnes
    return d.set_index("date")


# What differs between the two commodities; the trade pages read this instead of hard-coding coffee.
COMMS = {
    "coffee": dict(products="german_trade_products.csv", origins="german_trade_origins.csv", factor=GBE, main="Green",
                   item="Green coffee", units=["Tonnes", "'000 bags", "Million bags"], unit_default="'000 bags"),
    "cocoa": dict(products="german_cocoa_products.csv", origins="german_cocoa_origins.csv", factor=CBE, main="Beans",
                  item="Cocoa beans", units=["Tonnes", "'000 t"], unit_default="'000 t"),
}


@st.cache_data(ttl=3600)
def load_products(comm="coffee") -> pd.DataFrame:
    d = pd.read_csv(DB / COMMS[comm]["products"], parse_dates=["date"])
    d = d.groupby(["date", "product"], as_index=False).sum(numeric_only=True)        # chocolate = many HS codes
    d["gbe"] = d["product"].map(COMMS[comm]["factor"])
    d["cy"], d["cm"] = _cy(d["date"])
    return d


@st.cache_data(ttl=3600)
def load_origins(comm="coffee") -> pd.DataFrame:
    d = pd.read_csv(DB / COMMS[comm]["origins"], parse_dates=["date"])
    d["country"] = d["country"].map(clean_name)
    d["cy"], d["cm"] = _cy(d["date"])
    return d


@st.cache_data(ttl=3600)
def load_grind() -> pd.DataFrame:
    """Germany's quarterly cocoa grind, tonnes; crop year Oct-Sep, Q1 = Oct-Dec."""
    return pd.read_csv(DB / "german_cocoa_grind.csv")


def latest_month(d: pd.DataFrame, col="imp_t"):
    """Last month with a non-zero total: GENESIS publishes '...' for months not out yet, which the ingest skips."""
    g = d.groupby("date")[col].sum()
    return g[g > 0].index.max()


# ── Units ─────────────────────────────────────────────────────────────────────
UNITS = {"Tonnes": (1.0, ",.0f", "t"), "'000 bags": (1 / BAG_T / 1e3, ",.0f", "k bags"), "Million bags": (1 / BAG_T / 1e6, ",.2f", "M bags"),
         "'000 t": (1e-3, ",.1f", "k t")}


def unit_picker(key, comm="coffee"):
    opts = COMMS[comm]["units"]
    return st.radio("Unit", opts, index=opts.index(COMMS[comm]["unit_default"]), horizontal=True, key=f"{key}_{comm}")


def fmt_u(v, unit):
    f, fmt, suf = UNITS[unit]
    return f"{format(v * f, fmt)} {suf}"


# ── Plot base (COT_ALL: Plus Jakarta Sans 11, ticks 10) ───────────────────────
def ax(**kw):
    b = dict(showgrid=True, gridcolor=GRID, gridwidth=1, zeroline=True, zerolinecolor="rgba(0,0,0,0.12)", zerolinewidth=1,
             showline=True, linecolor="rgba(0,0,0,0.08)", linewidth=1, tickfont=dict(size=10, color=AXIS))
    b.update(kw)
    return b


def base(fig, height=380, legend="top", unified=True, **kw):
    leg = dict(orientation="h", x=0, y=1.0, yanchor="bottom", bgcolor="rgba(0,0,0,0)", font=dict(size=9.5),
               itemwidth=30, tracegroupgap=0)
    if legend == "bottom":
        leg.update(y=-0.12, yanchor="top")
    xaxis = ax(showgrid=False)
    xaxis.update(kw.pop("xaxis", {}))
    yaxis = ax()
    yaxis.update(kw.pop("yaxis", {}))
    margin = kw.pop("margin", dict(l=8, r=8, t=34 if legend == "top" else 10, b=8))
    fig.update_layout(template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Plus Jakarta Sans, sans-serif", color=INK, size=11), height=height,
                      margin=margin, legend=leg, showlegend=legend is not None,
                      hovermode="x unified" if unified else "closest", xaxis=xaxis, yaxis=yaxis,
                      hoverlabel=dict(font=dict(family="Plus Jakarta Sans, sans-serif", size=11)), **kw)
    return fig


def show(fig, key):
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False, "modeBarButtonsToRemove": ["select2d", "lasso2d"]})


def rgba(hex_, a):
    r, g, b = (int(hex_[k:k + 2], 16) for k in (1, 3, 5))
    return f"rgba({r},{g},{b},{a})"


# ── Page furniture ────────────────────────────────────────────────────────────
def hero(title, sub, chips=()):
    c = "".join(f"<span class='pt-chip'>{x}</span>" for x in chips)
    st.markdown(f"<div class='pt-head'><span class='pt-title'>{title}<span class='pt-sub'>{sub}</span></span>"
                f"<span class='pt-meta'>{c}</span></div>", unsafe_allow_html=True)


def card_head(title, desc=""):
    st.markdown(f"<div class='chart-head'>{title}</div>" + (f"<div class='card-desc'>{desc}</div>" if desc else ""),
                unsafe_allow_html=True)


def kpis(items):
    """items = [(label, value, sub, sign)] ; sign > 0 green, < 0 red, None grey."""
    out = []
    for lbl, val, sub, sign in items:
        cls = "" if sign is None or (isinstance(sign, float) and np.isnan(sign)) else ("up" if sign >= 0 else "dn")
        s = f"<span class='s {cls}'>{sub}</span>" if sub else ""
        out.append(f"<div class='kpi'><span class='l'>{lbl}</span><span class='v'>{val}</span>{s}</div>")
    st.markdown(f"<div class='kpis'>{''.join(out)}</div>", unsafe_allow_html=True)


def pct(a, b):
    return (a / b - 1) * 100 if b else np.nan


def signed(v, d=1):
    return "" if v is None or pd.isna(v) else f"{v:+.{d}f}%"


def table(header, rows, tot=None):
    """rows = [[(text, cls), ...]] ; first cell is the label."""
    h = "".join(f"<th>{x}</th>" for x in header)
    def tr(r, cls=""):
        cells = "".join(f"<td class='{c}'>{t}</td>" for t, c in r)
        return f"<tr class='{cls}'>{cells}</tr>"
    body = "".join(tr(r) for r in rows) + (tr(tot, "tot") if tot else "")
    st.markdown(f"<div class='tbl-scroll'><table class='gt'><tr>{h}</tr>{body}</table></div>", unsafe_allow_html=True)


def yoy_cell(v):
    return ("" if pd.isna(v) else f"{v:+.1f}%", "up" if pd.notna(v) and v >= 0 else "dn")


def cy_ytd(df, val, latest):
    """Coffee-year-to-date sums per crop year, cut at the latest month's crop-month position."""
    cm_now = (latest.month - 10) % 12 + 1
    return df[df["cm"] <= cm_now].groupby("cy")[val].sum(), cm_now
