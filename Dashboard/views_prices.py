"""Import prices: unit value of German green coffee imports (value / net mass, non-decaf) by origin.
Unit values trail futures: the coffee was priced months before it cleared customs."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (AMBER, AXIS, EUROPE, GREEN, LB_PER_T, NAVY, OTHER_C, RED, ROBUSTA, SERIES, TEAL, base, card_head,
                    hero, kpis, load_origins, latest_month, pct, rgba, show, signed, table)

CCY = {"USc/lb": ("imp_usd_k", 1e5 / LB_PER_T, ",.0f"), "EUR/kg": ("imp_eur_k", 1.0, ",.2f")}
MIN_T = 1000             # an origin needs this many tonnes in the window to get a price


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
    o["grp"] = np.where(o["country"].isin(ROBUSTA), "Robusta origins", "Arabica origins")

    g = o.groupby(["date", "grp"])[[col, "imp_t"]].sum().unstack()
    g = g.rolling(win).sum()
    a_ = _uv(g[col]["Arabica origins"], g["imp_t"]["Arabica origins"], k)
    r_ = _uv(g[col]["Robusta origins"], g["imp_t"]["Robusta origins"], k)
    t = o.groupby("date")[[col, "imp_t"]].sum().rolling(win).sum()
    tot = _uv(t[col], t["imp_t"], k)

    hero("Green coffee import prices", f" · unit value {ccy} · {smooth.lower()} volume-weighted",
         [f"Latest {last:%b %Y}", "Non-decaf, ex-Europe", "Destatis 51000-0018"])

    ago = last - pd.DateOffset(years=1)
    def at(s, d):
        return s.get(d, np.nan)
    spread, spread_ly = at(a_, last) - at(r_, last), at(a_, ago) - at(r_, ago)
    by = o.groupby(["date", "country"])[[col, "imp_t"]].sum().unstack().rolling(win).sum()
    def ctry(c, d):
        return _uv(by[col].get(c), by["imp_t"].get(c), k).get(d, np.nan) if c in by[col] else np.nan
    br, vn = ctry("Brazil", last), ctry("Vietnam", last)
    kpis([
        ("All green imports", format(at(tot, last), fmt), f"{signed(pct(at(tot, last), at(tot, ago)))} YoY", pct(at(tot, last), at(tot, ago))),
        ("Arabica origins", format(at(a_, last), fmt), f"{signed(pct(at(a_, last), at(a_, ago)))} YoY", pct(at(a_, last), at(a_, ago))),
        ("Robusta origins", format(at(r_, last), fmt), f"{signed(pct(at(r_, last), at(r_, ago)))} YoY", pct(at(r_, last), at(r_, ago))),
        ("Arabica − Robusta", format(spread, fmt), f"{format(spread - spread_ly, '+' + fmt[1:])} vs a year ago", spread - spread_ly),
        ("Brazil / Vietnam", f"{format(br, fmt)} / {format(vn, fmt)}", f"ratio {br / vn:.2f}x" if vn else "", None),
    ])

    # ── Row 1: Arabica vs Robusta | ranked latest ──
    l, r = st.columns([1.45, 1], gap="medium")
    with l, st.container(border=True):
        card_head("Arabica vs Robusta origins", f"Volume-weighted unit value, {ccy} · shaded = Arabica − Robusta spread (right axis)")
        sp = (a_ - r_).loc[since:]
        fig = go.Figure()
        fig.add_scatter(x=sp.index, y=sp.values, name="Spread", mode="lines", line=dict(width=0), fill="tozeroy",
                        fillcolor=rgba(TEAL, 0.16), yaxis="y2", hovertemplate=f"Spread: %{{y:{fmt}}}<extra></extra>")
        for s, nm, c, w in [(a_, "Arabica origins", NAVY, 2.4), (r_, "Robusta origins", AMBER, 2.4), (tot, "All", "#8a94a8", 1.3)]:
            s = s.loc[since:]
            fig.add_scatter(x=s.index, y=s.values, name=nm, mode="lines", line=dict(color=c, width=w),
                            hovertemplate=f"{nm}: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, 400, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt, title=dict(text=ccy, font=dict(size=10))),
                  yaxis2=dict(overlaying="y", side="right", showgrid=False, tickformat=fmt, rangemode="tozero",
                              tickfont=dict(size=10, color=TEAL), title=dict(text="spread", font=dict(size=10, color=TEAL)))), "ip_ar")

    lw = last - pd.DateOffset(months=2)
    lw_ly, last_ly = lw - pd.DateOffset(years=1), ago
    def window(a, b):
        w = o[(o["date"] >= a) & (o["date"] <= b)].groupby("country")[[col, "imp_t"]].sum()
        return w.assign(uv=_uv(w[col], w["imp_t"], k))
    now3, ly3 = window(lw, last), window(lw_ly, last_ly)
    now3 = now3[now3["imp_t"] >= MIN_T].sort_values("uv")

    with r, st.container(border=True):
        card_head(f"By origin, {lw:%b}–{last:%b %Y}", f"3-month unit value, origins with ≥{MIN_T:,} t · navy = Arabica, amber = Robusta, tick = a year ago")
        top = now3.tail(16)
        colors = [AMBER if c in ROBUSTA else NAVY for c in top.index]
        fig = go.Figure(go.Bar(y=top.index, x=top["uv"], orientation="h", marker_color=colors,
                               text=[format(v, fmt) for v in top["uv"]], textposition="outside", textfont=dict(size=9.5, color=AXIS),
                               cliponaxis=False, hovertemplate=f"%{{y}}: %{{x:{fmt}}} {ccy}<extra></extra>", name="Now"))
        fig.add_scatter(y=top.index, x=ly3["uv"].reindex(top.index), mode="markers", name="Year ago",
                        marker=dict(symbol="line-ns-open", size=14, line=dict(width=2.2, color=RED)),
                        hovertemplate=f"%{{y}} a year ago: %{{x:{fmt}}}<extra></extra>")
        show(base(fig, 400, unified=False, bargap=0.3, xaxis=dict(tickformat=fmt, showgrid=True), yaxis=dict(showgrid=False),
                  margin=dict(l=8, r=40, t=34, b=8)), "ip_rank")

    # ── Row 2: chosen origins | volume vs price change ──
    l, r = st.columns([1.45, 1], gap="medium")
    vol12 = o[o["date"] > last - pd.DateOffset(months=12)].groupby("country")["imp_t"].sum().sort_values(ascending=False)
    with l, st.container(border=True):
        h, c = st.columns([1, 1.6], vertical_alignment="center")
        with h:
            card_head("Origin price history", f"{smooth} volume-weighted, {ccy}")
        with c:
            pick = st.multiselect("Origins", vol12.index[:30].tolist(), default=[x for x in ["Brazil", "Vietnam", "Colombia", "Honduras", "Ethiopia", "Uganda"] if x in vol12.index],
                                  key="ip_pick", label_visibility="collapsed", max_selections=8)
        fig = go.Figure()
        for i, cn in enumerate(pick):
            s = _uv(by[col].get(cn), by["imp_t"].get(cn), k)
            s = s.where(by["imp_t"].get(cn) >= 100).loc[since:]                  # hide thin months
            fig.add_scatter(x=s.index, y=s.values, name=cn, mode="lines", connectgaps=False,
                            line=dict(color=SERIES[i % len(SERIES)], width=2), hovertemplate=f"{cn}: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, 400, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt, title=dict(text=ccy, font=dict(size=10)))), "ip_hist")

    with r, st.container(border=True):
        card_head("Price vs volume, last 12m vs prior 12m", "Each bubble an origin (size = 12m tonnes) · who got pricier and who Germany bought less of")
        def w12(a, b):
            w = o[(o["date"] > a) & (o["date"] <= b)].groupby("country")[[col, "imp_t"]].sum()
            return w.assign(uv=_uv(w[col], w["imp_t"], k))
        c12, p12 = w12(last - pd.DateOffset(months=12), last), w12(last - pd.DateOffset(months=24), last - pd.DateOffset(months=12))
        j = c12.join(p12, rsuffix="_p")
        j = j[(j["imp_t"] >= 5000) & (j["imp_t_p"] >= 5000)]
        j["dv"], j["dp"] = (j["imp_t"] / j["imp_t_p"] - 1) * 100, (j["uv"] / j["uv_p"] - 1) * 100
        fig = go.Figure(go.Scatter(x=j["dv"], y=j["dp"], mode="markers+text", text=j.index, textposition="top center",
                                   textfont=dict(size=9.5, color=AXIS),
                                   marker=dict(size=np.sqrt(j["imp_t"]) / np.sqrt(j["imp_t"].max()) * 44 + 6,
                                               color=[AMBER if c in ROBUSTA else NAVY for c in j.index], opacity=0.7,
                                               line=dict(color="#ffffff", width=1)),
                                   customdata=np.c_[j["imp_t"]],
                                   hovertemplate="%{text}<br>Volume %{x:+.0f}%<br>Price %{y:+.0f}%<br>%{customdata[0]:,.0f} t<extra></extra>"))
        fig.add_vline(x=0, line=dict(color="rgba(0,0,0,.2)", width=1))
        show(base(fig, 400, legend=None, unified=False, xaxis=dict(ticksuffix="%", showgrid=True, title=dict(text="volume change", font=dict(size=10))),
                  yaxis=dict(ticksuffix="%", title=dict(text="price change", font=dict(size=10)))), "ip_bub")

    # ── Table ──
    with st.container(border=True):
        card_head("Origin price table", f"{ccy} · 3-month windows, 12-month volume · origins with ≥{MIN_T:,} t in the last 3 months")
        rows = []
        for cn in now3.sort_values("imp_t", ascending=False).index[:20]:
            p_now, p_ly = now3.loc[cn, "uv"], ly3["uv"].get(cn, np.nan)
            ch = pct(p_now, p_ly)
            rows.append([(cn, "n"), ("Robusta" if cn in ROBUSTA else "Arabica", ""), (format(p_now, fmt), "b"),
                         (format(p_ly, fmt) if pd.notna(p_ly) else "", ""),
                         ("" if pd.isna(ch) else f"{ch:+.1f}%", "up" if pd.notna(ch) and ch >= 0 else "dn"),
                         (f"{vol12.get(cn, 0):,.0f}", ""), (f"{vol12.get(cn, 0) / vol12.sum() * 100:.1f}%", "")])
        table(["Origin", "Type", f"{lw:%b}–{last:%b %y}", f"{lw_ly:%b}–{last_ly:%b %y}", "YoY", "12m tonnes", "12m share"], rows)
        st.markdown("<div class='card-desc' style='margin-top:6px'>Unit value = customs value / net mass. It lags futures by the "
                    "shipping and pricing window (often 2–6 months) and mixes qualities and differentials, so read it as a trend.</div>",
                    unsafe_allow_html=True)
