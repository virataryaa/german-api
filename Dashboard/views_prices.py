"""Import prices: unit value (customs value / net mass) of German green coffee imports, non-decaf, ex-Europe.
Unit values trail futures: the coffee was priced months before it cleared customs."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (AMBER, AXIS, EUROPE, LB_PER_T, NAVY, RED, ROBUSTA, base, card_head, hero, kpis, latest_month,
                    load_origins, pct, show, signed)

CCY = {"USc/lb": ("imp_usd_k", 1e5 / LB_PER_T, ",.0f"), "EUR/kg": ("imp_eur_k", 1.0, ",.2f")}
MIN_T = 1000             # tonnes an origin needs in the 3-month window to be ranked


def render(ccy):
    col, k, fmt = CCY[ccy]
    o = load_origins()
    o = o[(o["product"] == "Green") & ~o["country"].isin(EUROPE) & (o["imp_t"] > 0)]
    last = latest_month(o)
    o = o[o["date"] <= last]
    o["grp"] = np.where(o["country"].isin(ROBUSTA), "Robusta", "Arabica")

    g = o.groupby(["date", "grp"])[[col, "imp_t"]].sum().unstack().rolling(3).sum()   # 3-month volume-weighted
    uv = (g[col] / g["imp_t"] * k).loc["2012-01-01":]
    ago = last - pd.DateOffset(years=1)

    hero("Green coffee import prices", f" · {ccy} · 3-month volume-weighted", [f"Latest {last:%b %Y}", "Customs value / net mass"])
    a, r_ = uv["Arabica"], uv["Robusta"]
    kpis([
        ("Arabica origins", format(a[last], fmt), f"{signed(pct(a[last], a[ago]))} YoY", pct(a[last], a[ago])),
        ("Robusta origins", format(r_[last], fmt), f"{signed(pct(r_[last], r_[ago]))} YoY", pct(r_[last], r_[ago])),
        ("Arabica − Robusta", format(a[last] - r_[last], fmt), f"a year ago {format(a[ago] - r_[ago], fmt)}", None),
    ])

    l, r = st.columns([1.3, 1], gap="medium")
    with l, st.container(border=True):
        card_head("Arabica vs Robusta origins", "Robusta origins = Vietnam, Uganda, Indonesia, India and peers")
        fig = go.Figure()
        fig.add_scatter(x=a.index, y=a, name="Arabica origins", mode="lines", line=dict(color=NAVY, width=2.2))
        fig.add_scatter(x=r_.index, y=r_, name="Robusta origins", mode="lines", line=dict(color=AMBER, width=2.2))
        show(base(fig, 420, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt, title=dict(text=ccy, font=dict(size=10)))), "ip_ar")
    with r, st.container(border=True):
        lo = last - pd.DateOffset(months=2)
        card_head(f"By origin, {lo:%b}–{last:%b %Y}", "Bar = now, red tick = a year earlier")
        def win(a_, b_):
            w = o[(o["date"] >= a_) & (o["date"] <= b_)].groupby("country")[[col, "imp_t"]].sum()
            return w.assign(uv=w[col] / w["imp_t"] * k)
        now, ly = win(lo, last), win(lo - pd.DateOffset(years=1), ago)
        now = now[now["imp_t"] >= MIN_T].sort_values("imp_t", ascending=False).head(12).sort_values("uv")
        fig = go.Figure(go.Bar(y=now.index, x=now["uv"], orientation="h", name="Now",
                               marker_color=[AMBER if c in ROBUSTA else NAVY for c in now.index],
                               text=[format(v, fmt) for v in now["uv"]], textposition="outside",
                               textfont=dict(size=9.5, color=AXIS), cliponaxis=False))
        fig.add_scatter(y=now.index, x=ly["uv"].reindex(now.index), mode="markers", name="Year ago",
                        marker=dict(symbol="line-ns-open", size=14, line=dict(width=2.2, color=RED)))
        show(base(fig, 420, legend=None, unified=False, bargap=0.3, xaxis=dict(tickformat=fmt, showgrid=True),
                  yaxis=dict(showgrid=False), margin=dict(l=8, r=40, t=10, b=8)), "ip_rank")
    st.caption("Unit values lag futures by the shipping and pricing window (often 2–6 months) and mix qualities, so read them as a trend.")
