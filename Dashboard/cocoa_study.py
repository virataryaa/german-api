"""Study: West Africa vs Latin America cocoa beans in German imports - price gap, volume share, and how they move together."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import (H, AMBER, AXIS, EUROPE, GREEN, GREY, NAVY, RED, SERIES, TEAL, base, card_head, hero, latest_month,
                    load_origins, pct, rgba, show, table, yoy_cell)
from views_prices import LATAM, WEST_AFRICA

CCY = {"USD/t": "imp_usd_k", "EUR/t": "imp_eur_k"}
LAGS = range(-6, 7)
COUNTRIES = ["Ecuador", "Peru", "Dominican Rep.", "Brazil", "Colombia"]
CORR_SET = ["Ivory Coast", "Ghana", "Nigeria", "Cameroon", "Ecuador", "Peru", "Dominican Rep."]


def sidebar():
    st.markdown("<div class='sb-lbl'>Study</div>", unsafe_allow_html=True)
    ccy = st.radio("Price unit", list(CCY), horizontal=True, key="cs_ccy")
    win = st.radio("Window", ["1m", "3m", "6m"], index=1, horizontal=True, key="cs_win")
    since = st.radio("History from", ["2006", "2012", "2018"], index=1, horizontal=True, key="cs_since")
    return ccy, int(win[:-1]), since


def _region_monthly(o, col):
    o = o.assign(reg=np.where(o["country"].isin(WEST_AFRICA), "WA", np.where(o["country"].isin(LATAM), "LA", None)))
    m = o.dropna(subset=["reg"]).groupby(["date", "reg"])[[col, "imp_t"]].sum().unstack().fillna(0)
    tot = o.groupby("date")["imp_t"].sum()
    return m, tot


def render(ccy, win, since):
    col = CCY[ccy]
    o = load_origins("cocoa")
    o = o[(o["product"] == "Beans") & ~o["country"].isin(EUROPE) & (o["imp_t"] > 0)]
    last = latest_month(o)
    o = o[o["date"] <= last]
    m, tot = _region_monthly(o, col)

    r3 = m.rolling(win).sum()                                       # volume-weighted over the window
    wa = r3[col]["WA"] / r3["imp_t"]["WA"] * 1e3
    la = r3[col]["LA"] / r3["imp_t"]["LA"] * 1e3
    gap = (la - wa)
    gap_pct = (la / wa - 1) * 100
    share = r3["imp_t"]["LA"] / tot.rolling(win).sum() * 100
    d = pd.DataFrame({"wa": wa, "la": la, "gap": gap, "gap_pct": gap_pct, "share": share}).dropna()
    dv = d.loc[since:]

    hero("Study: West Africa vs Latin America", f" · cocoa beans into Germany · {ccy} · {win}-month window", [f"Latest {last:%b %Y}"])

    # ── Row 1: prices + gap | gap vs Latin America share ──
    l, r = st.columns(2, gap="small")
    with l, st.container(border=True):
        card_head("Price by region and the gap")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.62, 0.38], vertical_spacing=0.06)
        fig.add_scatter(x=dv.index, y=dv["la"], name="Latin America", line=dict(color=AMBER, width=2.2), row=1, col=1)
        fig.add_scatter(x=dv.index, y=dv["wa"], name="West Africa", line=dict(color=NAVY, width=2.2), row=1, col=1)
        fig.add_bar(x=dv.index, y=dv["gap"], name="Gap (LatAm − WA)", marker_color=[TEAL if v >= 0 else RED for v in dv["gap"]],
                    row=2, col=1)
        base(fig, H + 40, bargap=0.1, xaxis=dict(tickformat="%Y"))
        fig.update_yaxes(tickformat=",.0f", gridcolor="rgba(10,36,99,0.08)", tickfont=dict(size=10, color=AXIS))
        fig.update_xaxes(showgrid=False, tickfont=dict(size=10, color=AXIS))
        show(fig, "cs_px")

    with r, st.container(border=True):
        card_head("Price gap % vs Latin America share of volume")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06)
        fig.add_scatter(x=dv.index, y=dv["gap_pct"], name="Gap %", line=dict(color=TEAL, width=2), row=1, col=1)
        fig.add_scatter(x=dv.index, y=dv["share"], name="LatAm share %", line=dict(color=AMBER, width=2),
                        fill="tozeroy", fillcolor=rgba(AMBER, 0.12), row=2, col=1)
        base(fig, H + 40, xaxis=dict(tickformat="%Y"))
        fig.update_yaxes(ticksuffix="%", gridcolor="rgba(10,36,99,0.08)", tickfont=dict(size=10, color=AXIS))
        fig.update_xaxes(showgrid=False, tickfont=dict(size=10, color=AXIS))
        show(fig, "cs_share")

    # ── Row 2: scatter | lead-lag ──
    q = m.loc[since:].resample("QS-OCT").sum()                      # cocoa-year quarters
    qd = pd.DataFrame({"gap_pct": (q[col]["LA"] / q["imp_t"]["LA"]) / (q[col]["WA"] / q["imp_t"]["WA"]) * 100 - 100,
                       "share": q["imp_t"]["LA"] / tot.loc[since:].resample("QS-OCT").sum() * 100}).dropna()
    qd = qd[qd.index + pd.offsets.QuarterEnd(0) <= last]           # complete quarters only
    l, r = st.columns(2, gap="small")
    with l, st.container(border=True):
        rho = qd["gap_pct"].corr(qd["share"])
        card_head(f"Gap % vs Latin America share, by quarter (r = {rho:.2f})")
        b, a = np.polyfit(qd["gap_pct"], qd["share"], 1)
        xs = np.linspace(qd["gap_pct"].min(), qd["gap_pct"].max(), 20)
        age = np.arange(len(qd)) / max(len(qd) - 1, 1)
        fig = go.Figure(go.Scatter(x=qd["gap_pct"], y=qd["share"], mode="markers", name="Quarter",
                                   marker=dict(size=8, color=age, colorscale=[[0, "#c3cbe0"], [1, NAVY]], line=dict(color="#fff", width=1)),
                                   text=[f"{i:%b %Y}" for i in qd.index],
                                   hovertemplate="%{text}<br>Gap %{x:.1f}%<br>LatAm share %{y:.1f}%<extra></extra>"))
        fig.add_scatter(x=xs, y=a + b * xs, mode="lines", name="Trend", line=dict(color=RED, dash="dot", width=1.6), hoverinfo="skip")
        fig.add_scatter(x=[qd["gap_pct"].iloc[-1]], y=[qd["share"].iloc[-1]], mode="markers+text", text=["latest"],
                        textposition="top center", marker=dict(size=12, color=AMBER, line=dict(color=NAVY, width=1.5)),
                        name="Latest", hoverinfo="skip", textfont=dict(size=9.5, color=AXIS))
        show(base(fig, H, legend=None, unified=False, xaxis=dict(ticksuffix="%", showgrid=True, title=dict(text="price gap %", font=dict(size=10))),
                  yaxis=dict(ticksuffix="%", title=dict(text="LatAm share", font=dict(size=10)))), "cs_scatter")

    with r, st.container(border=True):
        card_head("Lead / lag: change in gap vs change in LatAm share")
        x, y = d["gap_pct"].diff(12), d["share"].diff(12)          # year-on-year changes strip trend and season
        x, y = x.loc[since:], y.loc[since:]
        cors = pd.Series({k: x.shift(k).corr(y) for k in LAGS})
        best = cors.abs().idxmax()
        fig = go.Figure(go.Bar(x=cors.index, y=cors.values, marker_color=[NAVY if k == best else "#c3cbe0" for k in cors.index],
                               text=[f"{v:.2f}" for v in cors.values], textposition="outside", textfont=dict(size=9, color=AXIS),
                               cliponaxis=False, hovertemplate="lag %{x} m: r = %{y:.2f}<extra></extra>"))
        fig.add_hline(y=0, line=dict(color="rgba(0,0,0,.2)", width=1))
        show(base(fig, H, legend=None, unified=False, bargap=0.3,
                  xaxis=dict(dtick=1, title=dict(text="months the gap leads (+) / trails (−) the share", font=dict(size=10))),
                  yaxis=dict(range=[-1, 1], title=dict(text="correlation", font=dict(size=10)))), "cs_lag")

    # ── Row 3: country gaps | price correlation matrix ──
    l, r = st.columns([1.3, 1], gap="small")
    by = o.groupby(["date", "country"])[[col, "imp_t"]].sum().unstack().fillna(0).rolling(win).sum()
    wa_core = (by[col][["Ivory Coast", "Ghana"]].sum(axis=1) / by["imp_t"][["Ivory Coast", "Ghana"]].sum(axis=1)) * 1e3
    with l, st.container(border=True):
        card_head("Latin American origins vs Ivory Coast + Ghana, price gap")
        fig = go.Figure()
        for i, c in enumerate([c for c in COUNTRIES if c in by[col]]):
            uv = (by[col][c] / by["imp_t"][c] * 1e3).where(by["imp_t"][c] >= 150)
            g = (uv - wa_core).loc[since:]
            fig.add_scatter(x=g.index, y=g.values, name=c, mode="lines", connectgaps=False, line=dict(color=SERIES[i + 1], width=1.8),
                            hovertemplate=f"{c}: %{{y:,.0f}}<extra></extra>")
        fig.add_hline(y=0, line=dict(color="rgba(0,0,0,.25)", width=1))
        show(base(fig, H, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=",.0f")), "cs_ctry")

    with r, st.container(border=True):
        card_head("Price correlation between origins (monthly changes)")
        px = pd.DataFrame({c: (by[col][c] / by["imp_t"][c] * 1e3).where(by["imp_t"][c] >= 150)
                           for c in CORR_SET if c in by[col]}).loc[since:]
        cm = px.pct_change(fill_method=None).corr(min_periods=24)
        cm = cm.mask(np.eye(len(cm), dtype=bool))                  # blank the 1.00 diagonal
        fig = go.Figure(go.Heatmap(z=cm.values, x=cm.columns, y=cm.index, zmin=-1, zmax=1,
                                   colorscale=[[0, RED], [0.5, "#ffffff"], [1, NAVY]], showscale=False,
                                   text=[[f"{v:.2f}" if pd.notna(v) else "" for v in row] for row in cm.values],
                                   texttemplate="%{text}", textfont=dict(size=10), hovertemplate="%{y} × %{x}: %{z:.2f}<extra></extra>"))
        show(base(fig, H, legend=None, unified=False, xaxis=dict(tickangle=-35, tickfont=dict(size=9.5, color=AXIS), showline=False),
                  yaxis=dict(autorange="reversed", tickfont=dict(size=9.5, color=AXIS), showgrid=False, showline=False)), "cs_corr")

    # ── Table: by crop year ──
    with st.container(border=True):
        card_head("By crop year")
        yy = m.copy()
        yy["cy"] = [f"{(i.year - (i.month < 10)) % 100:02d}/{(i.year - (i.month < 10) + 1) % 100:02d}" for i in yy.index]
        t = yy.groupby("cy").sum()
        tt = tot.groupby(yy["cy"]).sum()
        t = t.iloc[-12:]
        rows, prev_gap = [], None
        for cy, r_ in t.iloc[::-1].iterrows():
            pwa, pla = r_[(col, "WA")] / r_[("imp_t", "WA")] * 1e3, r_[(col, "LA")] / r_[("imp_t", "LA")] * 1e3
            rows.append([(cy, "n"), (f"{pwa:,.0f}", ""), (f"{pla:,.0f}", ""), (f"{pla - pwa:,.0f}", "b"),
                         (f"{(pla / pwa - 1) * 100:+.1f}%", ""), (f"{r_[('imp_t', 'WA')]:,.0f}", ""),
                         (f"{r_[('imp_t', 'LA')]:,.0f}", ""), (f"{r_[('imp_t', 'LA')] / tt[cy] * 100:.1f}%", "b")])
        table(["Crop year", f"WA {ccy}", f"LatAm {ccy}", "Gap", "Gap %", "WA tonnes", "LatAm tonnes", "LatAm share"], rows)
