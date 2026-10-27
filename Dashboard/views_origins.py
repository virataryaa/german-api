"""Origins: German green coffee imports (incl. decaf) by country of origin (51000-0018), coffee year Oct-Sep."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (AXIS, EUROPE, GREEN, MONTHS, NAVY, OTHER_C, RED, ROBUSTA, SERIES, UNITS, base, card_head, cy_ytd,
                    fmt_u, hero, kpis, latest_month, load_origins, pct, show, signed)


def render(unit):
    f, fmt, suf = UNITS[unit]
    d = load_origins()
    d = d[~d["country"].isin(EUROPE)]                       # intra-Europe flows are re-shipments, not origins
    last = latest_month(d)
    d = d[d["date"] <= last]
    cys = sorted(d["cy"].unique())
    cur, prev = d.loc[d["date"] == last, "cy"].iloc[0], None
    prev = cys[cys.index(cur) - 1]
    _, cm = cy_ytd(d, "imp_t", last)
    cut = f"Oct–{MONTHS[cm - 1]}"
    by = d[d["cm"] <= cm].groupby(["cy", "country"])["imp_t"].sum()
    c_, p_ = by.loc[cur], by.loc[prev]
    tc, tp = c_.sum(), p_.sum()

    hero("Green coffee imports by origin", f" · {unit}", [f"Latest {last:%b %Y}", "Excl. European re-shipments"])

    rob_c, rob_p = c_[c_.index.isin(ROBUSTA)].sum() / tc * 100, p_[p_.index.isin(ROBUSTA)].sum() / tp * 100
    br_c, br_p = c_.get("Brazil", 0) / tc * 100, p_.get("Brazil", 0) / tp * 100
    kpis([
        (f"{cur} to date ({cut})", fmt_u(tc, unit), f"{signed(pct(tc, tp))} vs {prev}", pct(tc, tp)),
        ("Brazil share", f"{br_c:.0f}%", f"{br_c - br_p:+.1f} pp", br_c - br_p),
        ("Robusta-origin share", f"{rob_c:.0f}%", f"{rob_c - rob_p:+.1f} pp", rob_c - rob_p),
    ])

    l, r = st.columns(2, gap="medium")
    with l, st.container(border=True):
        card_head(f"By origin, {cut}", f"{cur} vs {prev} · change in label")
        b = pd.DataFrame({"cur": c_, "prev": p_}).fillna(0)
        b = b.loc[b["cur"].sort_values(ascending=False).index[:12]].iloc[::-1]
        fig = go.Figure()
        fig.add_bar(y=b.index, x=b["prev"] * f, name=prev, orientation="h", marker_color=OTHER_C)
        fig.add_bar(y=b.index, x=b["cur"] * f, name=cur, orientation="h", marker_color=NAVY)
        for c, row in b.iterrows():
            ch = pct(row["cur"], row["prev"])
            if pd.notna(ch) and np.isfinite(ch):
                fig.add_annotation(y=c, x=max(row["cur"], row["prev"]) * f, text=f"{ch:+.0f}%", showarrow=False, xanchor="left",
                                   xshift=4, font=dict(size=10, color=GREEN if ch >= 0 else RED))
        show(base(fig, 440, barmode="group", bargap=0.3, bargroupgap=0.05, unified=False, xaxis=dict(tickformat=fmt, showgrid=True),
                  yaxis=dict(showgrid=False), margin=dict(l=8, r=40, t=34, b=8)), "or_ytd")
    with r, st.container(border=True):
        top = c_.sort_values(ascending=False).index[:5].tolist()
        card_head("12-month rolling, top 5 origins", "Trailing 12-month imports per origin")
        m = d.groupby(["date", "country"])["imp_t"].sum().unstack(fill_value=0).sort_index()
        roll = m[top].rolling(12).sum().loc["2010-01-01":] * f
        fig = go.Figure()
        for i, c in enumerate(top):
            fig.add_scatter(x=roll.index, y=roll[c], name=c, mode="lines", line=dict(color=SERIES[i], width=2))
        show(base(fig, 440, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "or_roll")
