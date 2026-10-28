"""Study: two groups of cocoa origins (default West Africa vs Latin America) in German bean imports -
price gap, volume share, how they move together, and each origin's price against a chosen base origin."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from common import (H, AMBER, AXIS, EUROPE, NAVY, RED, SERIES, TEAL, base, card_head, hero, latest_month, load_origins,
                    rgba, show, table)
from views_prices import LATAM, WEST_AFRICA

CCY = {"USD/t": "imp_usd_k", "EUR/t": "imp_eur_k"}
LAGS = range(-12, 13)
CORR_SET = ["Ivory Coast", "Ghana", "Nigeria", "Cameroon", "Ecuador", "Peru", "Dominican Rep."]
MIN_T = 150              # tonnes in the window for an origin's price to count
FILL = 3                 # months of missing price bridged by straight-line fill


def _beans():
    o = load_origins("cocoa")
    return o[(o["product"] == "Beans") & ~o["country"].isin(EUROPE) & (o["imp_t"] > 0)]


def _label(sel, default, name):
    return name if set(sel) == set(default) else " + ".join(sel) if len(sel) <= 3 else f"{sel[0]} + {len(sel) - 1} more"


def sidebar():
    st.markdown("<div class='sb-lbl'>Study</div>", unsafe_allow_html=True)
    ccy = st.radio("Price unit", list(CCY), horizontal=True, key="cs_ccy")
    win = st.radio("Window", ["1m", "3m", "6m"], index=1, horizontal=True, key="cs_win")
    since = st.radio("History from", ["2006", "2012", "2018"], index=1, horizontal=True, key="cs_since")
    vol = _beans().groupby("country")["imp_t"].sum().sort_values(ascending=False)
    opts = vol.index.tolist()
    da, db = [c for c in opts if c in WEST_AFRICA], [c for c in opts if c in LATAM]
    a = st.multiselect("Group A", opts, default=da, key="cs_ga")
    b = st.multiselect("Group B", [c for c in opts if c not in a], default=[c for c in db if c not in a], key="cs_gb")
    return ccy, int(win[:-1]), since, a or da, b or db, _label(a or da, da, "West Africa"), _label(b or db, db, "Latin America")


def _uv(val, t):
    return val / t.replace(0, np.nan) * 1e3


def render(ccy, win, since, ga, gb, na, nb):
    col = CCY[ccy]
    o = _beans()
    last = latest_month(o)
    o = o[o["date"] <= last]
    by_m = o.groupby(["date", "country"])[[col, "imp_t"]].sum().unstack().fillna(0)
    tot = by_m["imp_t"].sum(axis=1)

    def grp(cs):
        return by_m[col].reindex(columns=cs, fill_value=0).sum(axis=1), by_m["imp_t"].reindex(columns=cs, fill_value=0).sum(axis=1)

    (va, ta), (vb, tb) = grp(ga), grp(gb)
    pa = _uv(va.rolling(win).sum(), ta.rolling(win).sum())
    pb = _uv(vb.rolling(win).sum(), tb.rolling(win).sum())
    d = pd.DataFrame({"a": pa, "b": pb, "gap": pb - pa, "gap_pct": (pb / pa - 1) * 100,
                      "share": tb.rolling(win).sum() / tot.rolling(win).sum() * 100}).dropna()
    dv = d.loc[since:]

    hero(f"Study: {na} vs {nb}", f" · cocoa beans into Germany · {ccy} · {win}-month window", [f"Latest {last:%b %Y}"])

    # ── Row 1: prices + gap | gap vs B's share ──
    l, r = st.columns(2, gap="small")
    with l, st.container(border=True):
        card_head(f"Price by group and the gap ({nb} − {na})")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.62, 0.38], vertical_spacing=0.06)
        fig.add_scatter(x=dv.index, y=dv["b"], name=nb, line=dict(color=AMBER, width=2.2), row=1, col=1)
        fig.add_scatter(x=dv.index, y=dv["a"], name=na, line=dict(color=NAVY, width=2.2), row=1, col=1)
        fig.add_bar(x=dv.index, y=dv["gap"], name="Gap", marker_color=[TEAL if v >= 0 else RED for v in dv["gap"]], row=2, col=1)
        base(fig, H + 40, bargap=0.1, xaxis=dict(tickformat="%Y"))
        fig.update_yaxes(tickformat=",.0f", gridcolor="rgba(10,36,99,0.08)", tickfont=dict(size=10, color=AXIS))
        fig.update_xaxes(showgrid=False, tickfont=dict(size=10, color=AXIS))
        show(fig, "cs_px")

    with r, st.container(border=True):
        card_head(f"Price gap % vs {nb} share of volume")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.06)
        fig.add_scatter(x=dv.index, y=dv["gap_pct"], name="Gap %", line=dict(color=TEAL, width=2), row=1, col=1)
        fig.add_scatter(x=dv.index, y=dv["share"], name=f"{nb} share %", line=dict(color=AMBER, width=2),
                        fill="tozeroy", fillcolor=rgba(AMBER, 0.12), row=2, col=1)
        base(fig, H + 40, xaxis=dict(tickformat="%Y"))
        fig.update_yaxes(ticksuffix="%", gridcolor="rgba(10,36,99,0.08)", tickfont=dict(size=10, color=AXIS))
        fig.update_xaxes(showgrid=False, tickfont=dict(size=10, color=AXIS))
        show(fig, "cs_share")

    # ── Row 2: scatter (optional best lag) | lead-lag (levels or YoY changes) ──
    l, r = st.columns(2, gap="small")
    with l, st.container(border=True):
        h, c = st.columns([1.3, 1], vertical_alignment="center")
        with c:
            lag_mode = st.radio("Lag", ["No lag", "Best lag ±12m"], horizontal=True, key="cs_lagmode", label_visibility="collapsed")
        lag_r = pd.Series({k: dv["gap_pct"].shift(k).corr(dv["share"]) for k in LAGS})
        k = int(lag_r.abs().idxmax()) if lag_mode != "No lag" else 0
        sd = pd.DataFrame({"x": dv["gap_pct"].shift(k), "y": dv["share"]}).dropna()
        rho = sd["x"].corr(sd["y"])
        lag_txt = "" if k == 0 else f", gap {abs(k)}m {'earlier' if k > 0 else 'later'}"
        with h:
            card_head(f"Gap % vs {nb} share ({win}m{lag_txt}, r = {rho:.2f})")
        bb, aa = np.polyfit(sd["x"], sd["y"], 1)
        xs = np.linspace(sd["x"].min(), sd["x"].max(), 20)
        age = np.arange(len(sd)) / max(len(sd) - 1, 1)
        fig = go.Figure(go.Scatter(x=sd["x"], y=sd["y"], mode="markers", name="Month",
                                   marker=dict(size=7, color=age, colorscale=[[0, "#c3cbe0"], [1, NAVY]], line=dict(color="#fff", width=0.8)),
                                   text=[f"{i:%b %Y}" for i in sd.index],
                                   hovertemplate="%{text}<br>Gap %{x:.1f}%<br>Share %{y:.1f}%<extra></extra>"))
        fig.add_scatter(x=xs, y=aa + bb * xs, mode="lines", name="Trend", line=dict(color=RED, dash="dot", width=1.6), hoverinfo="skip")
        fig.add_scatter(x=[sd["x"].iloc[-1]], y=[sd["y"].iloc[-1]], mode="markers+text", text=["latest"], textposition="top center",
                        marker=dict(size=12, color=AMBER, line=dict(color=NAVY, width=1.5)), name="Latest", hoverinfo="skip",
                        textfont=dict(size=9.5, color=AXIS))
        show(base(fig, H, legend=None, unified=False, xaxis=dict(ticksuffix="%", showgrid=True, title=dict(text="price gap %", font=dict(size=10))),
                  yaxis=dict(ticksuffix="%", title=dict(text=f"{nb} share", font=dict(size=10)))), "cs_scatter")

    with r, st.container(border=True):
        h, c = st.columns([1.3, 1], vertical_alignment="center")
        with c:
            mode = st.radio("Basis", ["Levels", "YoY changes"], horizontal=True, key="cs_lagbasis", label_visibility="collapsed")
        with h:
            card_head(f"Lead / lag: gap % vs {nb} share")
        x, y = (d["gap_pct"], d["share"]) if mode == "Levels" else (d["gap_pct"].diff(12), d["share"].diff(12))
        x, y = x.loc[since:], y.loc[since:]
        cors = pd.Series({k_: x.shift(k_).corr(y) for k_ in LAGS})
        best = cors.abs().idxmax()
        fig = go.Figure(go.Bar(x=cors.index, y=cors.values, marker_color=[NAVY if k_ == best else "#c3cbe0" for k_ in cors.index],
                               text=[f"{v:.2f}" for v in cors.values], textposition="outside", textfont=dict(size=8.5, color=AXIS),
                               cliponaxis=False, hovertemplate="lag %{x} m: r = %{y:.2f}<extra></extra>"))
        fig.add_hline(y=0, line=dict(color="rgba(0,0,0,.2)", width=1))
        show(base(fig, H, legend=None, unified=False, bargap=0.3,
                  xaxis=dict(dtick=2, title=dict(text="months the gap leads (+) / trails (−) the share", font=dict(size=10))),
                  yaxis=dict(range=[-1, 1], title=dict(text="correlation", font=dict(size=10)))), "cs_lag")

    # ── Row 3: every origin against a chosen base ──
    by = by_m.rolling(win).sum()

    def price(c):
        p_ = _uv(by[col][c], by["imp_t"][c]).where(by["imp_t"][c] >= MIN_T)
        return p_.interpolate(limit=FILL, limit_area="inside")     # bridge short gaps from thin months

    vol = by_m["imp_t"].sum().sort_values(ascending=False)
    opts = [c for c in vol.index if (by_m["imp_t"][c] > 0).sum() >= 24]
    with st.container(border=True):
        h, c1, c2 = st.columns([1.2, 0.8, 2.2], vertical_alignment="center")
        with c1:
            base_c = st.selectbox("Base", opts, index=opts.index("Ivory Coast") if "Ivory Coast" in opts else 0, key="cs_base",
                                  label_visibility="collapsed")
        with c2:
            dflt = [x for x in ["Ghana", "Nigeria", "Cameroon", "Ecuador", "Peru", "Dominican Rep."] if x in opts and x != base_c]
            comp = st.multiselect("Compare", [x for x in opts if x != base_c], default=dflt, key="cs_comp",
                                  label_visibility="collapsed", max_selections=8)
        with h:
            card_head(f"Price gap vs {base_c}")
        bp = price(base_c)
        fig = go.Figure()
        for i, cn in enumerate(comp):
            g = (price(cn) - bp).loc[since:]
            fig.add_scatter(x=g.index, y=g.values, name=cn, mode="lines", line=dict(color=SERIES[(i + 1) % len(SERIES)], width=1.8),
                            hovertemplate=f"{cn}: %{{y:,.0f}}<extra></extra>")
        fig.add_hline(y=0, line=dict(color="rgba(0,0,0,.25)", width=1))
        show(base(fig, 300, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=",.0f", title=dict(text=ccy, font=dict(size=10)))), "cs_ctry")

    # ── Row 4: correlation of price levels | of price changes ──
    px = pd.DataFrame({c: price(c) for c in CORR_SET if c in by[col]}).loc[since:]
    l, r = st.columns(2, gap="small")
    for box, title, frame, key in [(l, "Price correlation between origins (price levels)", px, "cs_corr_lvl"),
                                   (r, "Price correlation between origins (monthly changes)", px.pct_change(fill_method=None), "cs_corr")]:
        with box, st.container(border=True):
            card_head(title)
            cm = frame.corr(min_periods=24)
            cm = cm.mask(np.eye(len(cm), dtype=bool))              # blank the 1.00 diagonal
            vals = cm.stack()                                      # soft scale over this matrix's own range
            fig = go.Figure(go.Heatmap(z=cm.values, x=cm.columns, y=cm.index, zmin=float(vals.min()), zmax=float(vals.max()),
                                       colorscale=[[0, "#fbfcfe"], [0.5, "#dbe6f5"], [1, "#9fbbe3"]], showscale=False,
                                       text=[[f"{v:.2f}" if pd.notna(v) else "" for v in row] for row in cm.values],
                                       texttemplate="%{text}", textfont=dict(size=10, color="#1a1a2e"),
                                       hovertemplate="%{y} × %{x}: %{z:.2f}<extra></extra>", xgap=2, ygap=2))
            show(base(fig, H, legend=None, unified=False, xaxis=dict(tickangle=-35, tickfont=dict(size=9.5, color=AXIS), showline=False),
                      yaxis=dict(autorange="reversed", tickfont=dict(size=9.5, color=AXIS), showgrid=False, showline=False)), key)

    # ── Table: by crop year ──
    with st.container(border=True):
        card_head("By crop year")
        cy = pd.Series([f"{(i.year - (i.month < 10)) % 100:02d}/{(i.year - (i.month < 10) + 1) % 100:02d}" for i in by_m.index], index=by_m.index)
        t = pd.DataFrame({"va": va, "ta": ta, "vb": vb, "tb": tb, "tot": tot}).groupby(cy).sum().iloc[-12:]
        rows = []
        for c_, r_ in t.iloc[::-1].iterrows():
            p_a, p_b = r_["va"] / r_["ta"] * 1e3, r_["vb"] / r_["tb"] * 1e3
            rows.append([(c_, "n"), (f"{p_a:,.0f}", ""), (f"{p_b:,.0f}", ""), (f"{p_b - p_a:,.0f}", "b"), (f"{(p_b / p_a - 1) * 100:+.1f}%", ""),
                         (f"{r_['ta']:,.0f}", ""), (f"{r_['tb']:,.0f}", ""), (f"{r_['tb'] / r_['tot'] * 100:.1f}%", "b")])
        table(["Crop year", f"{na} {ccy}", f"{nb} {ccy}", "Gap", "Gap %", f"{na} t", f"{nb} t", f"{nb} share"], rows)
