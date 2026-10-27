"""Import prices: unit value of German green coffee imports (value / net mass, non-decaf) by origin.
Unit values trail futures: the coffee was priced months before it cleared customs."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (H, AMBER, AXIS, EUROPE, GREY, LB_PER_T, NAVY, RED, ROBUSTA, SERIES, TEAL, base, card_head, hero,
                    load_origins, latest_month, pct, show, table)

CCY = {"USc/lb": ("imp_usd_k", 1e5 / LB_PER_T, ",.0f"), "EUR/kg": ("imp_eur_k", 1.0, ",.2f")}
MIN_T = 1000             # an origin needs this many tonnes in the window to get a price
# Customs codes do not split Arabica from Robusta, so origins are grouped by what they mostly grow.
# Brazil ships both (Arabica + Conilon) and is a third of the volume, so it gets its own line.
ARA, ROB, BRA = "Mainly Arabica origins", "Mainly Robusta origins", "Brazil"
GROUP_C = {ARA: NAVY, ROB: AMBER, BRA: TEAL}


def group(country):
    return BRA if country == "Brazil" else ROB if country in ROBUSTA else ARA


def sidebar():
    st.markdown("<div class='sb-lbl'>Import prices</div>", unsafe_allow_html=True)
    ccy = st.radio("Price unit", list(CCY), horizontal=True, key="ip_ccy")
    smooth = st.radio("Smoothing", ["Monthly", "3m", "6m"], index=1, horizontal=True, key="ip_smooth")
    since = st.radio("History from", ["2010", "2016", "2020"], index=1, horizontal=True, key="ip_since")
    return ccy, smooth, since


def _uv(val, t, k):
    return val / t.replace(0, np.nan) * k


def render(ccy, smooth, since):
    col, k, fmt = CCY[ccy]
    win = 1 if smooth == "Monthly" else int(smooth[:-1])
    o = load_origins()
    o = o[(o["product"] == "Green") & ~o["country"].isin(EUROPE) & (o["imp_t"] > 0)]
    last = latest_month(o)
    o = o[o["date"] <= last]
    o["grp"] = o["country"].map(group)

    g = o.groupby(["date", "grp"])[[col, "imp_t"]].sum().unstack()
    g = g.rolling(win).sum()
    grp_uv = {n: _uv(g[col][n], g["imp_t"][n], k) for n in (ARA, ROB, BRA)}
    t = o.groupby("date")[[col, "imp_t"]].sum().rolling(win).sum()
    tot = _uv(t[col], t["imp_t"], k)

    hero("Green coffee import prices", f" · unit value {ccy} · {smooth.lower()} volume-weighted",
         [f"Latest {last:%b %Y}"])

    ago = last - pd.DateOffset(years=1)
    by = o.groupby(["date", "country"])[[col, "imp_t"]].sum().unstack().rolling(win).sum()

    # ── Row 1: Arabica vs Robusta | chosen origins ──
    l, r = st.columns(2, gap="small")
    with l, st.container(border=True):
        card_head("Mainly Arabica vs mainly Robusta origins")
        fig = go.Figure()
        for s_, nm, c, w in [(grp_uv[ARA], ARA, NAVY, 2.4), (grp_uv[ROB], ROB, AMBER, 2.4), (grp_uv[BRA], BRA, TEAL, 2),
                             (tot, "All", GREY, 1.2)]:
            s_ = s_.loc[since:]
            fig.add_scatter(x=s_.index, y=s_.values, name=nm, mode="lines", line=dict(color=c, width=w),
                            hovertemplate=f"{nm}: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, H, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "ip_ar")

    vol12 = o[o["date"] > last - pd.DateOffset(months=12)].groupby("country")["imp_t"].sum().sort_values(ascending=False)
    with r, st.container(border=True):
        h, c = st.columns([1, 1.6], vertical_alignment="center")
        with h:
            card_head("Origin price history")
        with c:
            pick = st.multiselect("Origins", vol12.index[:30].tolist(), default=[x for x in ["Brazil", "Vietnam", "Colombia", "Honduras", "Ethiopia", "Uganda"] if x in vol12.index],
                                  key="ip_pick", label_visibility="collapsed", max_selections=8)
        fig = go.Figure()
        for i, cn in enumerate(pick):
            s_ = _uv(by[col].get(cn), by["imp_t"].get(cn), k)
            s_ = s_.where(by["imp_t"].get(cn) >= 100).loc[since:]                  # hide thin months
            fig.add_scatter(x=s_.index, y=s_.values, name=cn, mode="lines", connectgaps=False,
                            line=dict(color=SERIES[i % len(SERIES)], width=2), hovertemplate=f"{cn}: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, H, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "ip_hist")

    # ── Row 2: price by origin, now vs a year ago ──
    lw = last - pd.DateOffset(months=2)
    lw_ly, last_ly = lw - pd.DateOffset(years=1), ago
    def window(a, b):
        w = o[(o["date"] >= a) & (o["date"] <= b)].groupby("country")[[col, "imp_t"]].sum()
        return w.assign(uv=_uv(w[col], w["imp_t"], k))
    now3, ly3 = window(lw, last), window(lw_ly, last_ly)
    now3 = now3[now3["imp_t"] >= MIN_T].sort_values("uv")
    with st.container(border=True):
        card_head(f"Price by origin, {lw:%b}–{last:%b %Y} vs a year ago")
        top = now3.sort_values("imp_t").tail(16).sort_values("uv", ascending=False)
        fig = go.Figure(go.Bar(x=top.index, y=top["uv"], marker_color=[GROUP_C[group(c)] for c in top.index],
                               text=[format(v, fmt) for v in top["uv"]], textposition="outside", textfont=dict(size=9.5, color=AXIS),
                               cliponaxis=False, hovertemplate=f"%{{x}}: %{{y:{fmt}}} {ccy}<extra></extra>", name="Now"))
        fig.add_scatter(x=top.index, y=ly3["uv"].reindex(top.index), mode="markers", name="Year ago",
                        marker=dict(symbol="line-ew-open", size=22, line=dict(width=2.4, color=RED)),
                        hovertemplate=f"%{{x}} a year ago: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, 290, unified=False, bargap=0.35, xaxis=dict(tickfont=dict(size=9.5, color=AXIS)),
                  yaxis=dict(tickformat=fmt)), "ip_rank")

    # ── Table ──
    with st.container(border=True):
        card_head("Origin price table")
        rows = []
        for cn in now3.sort_values("imp_t", ascending=False).index[:20]:
            p_now, p_ly = now3.loc[cn, "uv"], ly3["uv"].get(cn, np.nan)
            ch = pct(p_now, p_ly)
            rows.append([(cn, "n"), ({ARA: "Mainly Arabica", ROB: "Mainly Robusta", BRA: "Both"}[group(cn)], ""), (format(p_now, fmt), "b"),
                         (format(p_ly, fmt) if pd.notna(p_ly) else "", ""),
                         ("" if pd.isna(ch) else f"{ch:+.1f}%", "up" if pd.notna(ch) and ch >= 0 else "dn"),
                         (f"{vol12.get(cn, 0):,.0f}", ""), (f"{vol12.get(cn, 0) / vol12.sum() * 100:.1f}%", "")])
        table(["Origin", "Type", f"{lw:%b}–{last:%b %y}", f"{lw_ly:%b}–{last_ly:%b %y}", "YoY", "12m tonnes", "12m share"], rows)
