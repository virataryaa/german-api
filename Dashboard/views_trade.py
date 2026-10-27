"""Trade balance: German coffee imports, re-exports and net imports in green-bean equivalent (ICO factors:
roasted x1.19, soluble x2.6), set against coffee-tax implied consumption. The gap is an implied stock change."""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from common import (AMBER, AXIS, GBE, GREEN, GREY, MONTHS, NAVY, OTHER_C, RED, SERIES, TEAL, UNITS, WINE, base,
                    card_head, fmt_u, hero, kpis, load_origins, load_products, load_tax, latest_month, pct, show,
                    signed, table, unit_picker, yoy_cell)

PRODUCTS = list(GBE)


def sidebar():
    st.markdown("<div class='sb-lbl'>Trade balance</div>", unsafe_allow_html=True)
    unit = unit_picker("tb_unit")
    since = st.radio("History from", ["2010", "2016", "2020"], index=1, horizontal=True, key="tb_since")
    return unit, since


def _monthly():
    """date x {imp_gbe, exp_gbe, net_gbe, cons} in tonnes GBE, plus per-product imports/exports in GBE."""
    p = load_products().copy()
    p["imp_g"], p["exp_g"] = p["imp_t"] * p["gbe"], p["exp_t"] * p["gbe"]
    last = min(latest_month(p), load_tax().index.max())
    p = p[p["date"] <= last]
    imp = p.pivot_table(index="date", columns="product", values="imp_g", aggfunc="sum").reindex(columns=PRODUCTS).fillna(0)
    exp = p.pivot_table(index="date", columns="product", values="exp_g", aggfunc="sum").reindex(columns=PRODUCTS).fillna(0)
    m = pd.DataFrame({"imp": imp.sum(axis=1), "exp": exp.sum(axis=1)})
    m["net"] = m["imp"] - m["exp"]
    m["cons"] = load_tax()["cons_t"].reindex(m.index)
    m["gap"] = m["net"] - m["cons"]
    return m, imp, exp, last


def render(unit, since):
    f, fmt, suf = UNITS[unit]
    m, imp, exp, last = _monthly()
    w12 = m.loc[last - pd.DateOffset(months=11):last]
    p12 = m.loc[last - pd.DateOffset(months=23):last - pd.DateOffset(months=12)]
    i12, e12 = imp.loc[w12.index].sum(), exp.loc[w12.index].sum()

    hero("Trade balance and implied stocks", f" · green-bean equivalent · {unit}",
         [f"Latest {last:%b %Y}", "Roasted x1.19 · Soluble x2.6", "Destatis 51000-0014 + 71211-0005"])

    s = w12.sum()
    sp = p12.sum()
    kpis([
        ("Gross imports, 12m", fmt_u(s["imp"], unit), f"{signed(pct(s['imp'], sp['imp']))} YoY", pct(s["imp"], sp["imp"])),
        ("Re-exports, 12m", fmt_u(s["exp"], unit), f"{s['exp'] / s['imp'] * 100:.0f}% of imports", None),
        ("Net imports, 12m", fmt_u(s["net"], unit), f"{signed(pct(s['net'], sp['net']))} YoY", pct(s["net"], sp["net"])),
        ("Tax consumption, 12m", fmt_u(s["cons"], unit), f"{signed(pct(s['cons'], sp['cons']))} YoY", pct(s["cons"], sp["cons"])),
        ("Implied stock change, 12m", fmt_u(s["gap"], unit), "net imports − consumption", s["gap"]),
    ])

    # ── Row 1: waterfall | net imports vs consumption ──
    l, r = st.columns([1, 1.35], gap="medium")
    with l, st.container(border=True):
        card_head(f"Where the coffee went, 12m to {last:%b %Y}", "Imports in, re-exports out, consumption out = implied stock change")
        steps = [("Green imp", i12["Green"] + i12["Green decaf"]), ("Roasted imp", i12["Roasted"] + i12["Roasted decaf"]),
                 ("Soluble imp", i12["Soluble"]), ("Green exp", -(e12["Green"] + e12["Green decaf"])),
                 ("Roasted exp", -(e12["Roasted"] + e12["Roasted decaf"])), ("Soluble exp", -e12["Soluble"])]
        x = [a for a, _ in steps] + ["Net imports", "Consumption", "Stock chg"]
        y = [v * f for _, v in steps] + [0, -s["cons"] * f, 0]
        meas = ["relative"] * 6 + ["total", "relative", "total"]
        fig = go.Figure(go.Waterfall(x=x, y=y, measure=meas, connector=dict(line=dict(color="rgba(10,36,99,.25)", width=1)),
                                     increasing=dict(marker=dict(color=TEAL)), decreasing=dict(marker=dict(color=RED)),
                                     totals=dict(marker=dict(color=NAVY)),
                                     text=[format(abs(v), fmt) if v else "" for v in y[:7]] + [format(-y[7], fmt), format(s["gap"] * f, fmt)],
                                     textposition="outside", textfont=dict(size=9.5, color=AXIS), cliponaxis=False,
                                     hovertemplate=f"%{{x}}: %{{y:{fmt}}} {suf}<extra></extra>"))
        show(base(fig, 400, legend=None, unified=False, xaxis=dict(tickfont=dict(size=9.5, color=AXIS)),
                  yaxis=dict(tickformat=fmt, title=dict(text=suf, font=dict(size=10)))), "tb_wf")

    with r, st.container(border=True):
        card_head("Net imports vs tax consumption, 12m rolling", "Bars = implied stock build (+) / draw (−), trailing 12 months")
        roll = m.rolling(12).sum().loc[since:] * f
        fig = go.Figure()
        fig.add_bar(x=roll.index, y=roll["gap"], name="Stock change", marker_color=[TEAL if v >= 0 else RED for v in roll["gap"].fillna(0)],
                    opacity=0.55, hovertemplate=f"Gap: %{{y:{fmt}}} {suf}<extra></extra>", yaxis="y2")
        fig.add_scatter(x=roll.index, y=roll["net"], name="Net imports", mode="lines", line=dict(color=NAVY, width=2.4),
                        hovertemplate=f"Net imports: %{{y:{fmt}}}<extra></extra>")
        fig.add_scatter(x=roll.index, y=roll["cons"], name="Tax consumption", mode="lines", line=dict(color=AMBER, width=2.4),
                        hovertemplate=f"Consumption: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, 400, bargap=0.05, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt, title=dict(text=f"12m {suf}", font=dict(size=10))),
                  yaxis2=dict(overlaying="y", side="right", showgrid=False, tickformat=fmt, zeroline=True,
                              zerolinecolor="rgba(0,0,0,.15)", tickfont=dict(size=10, color=GREY),
                              title=dict(text="stock chg", font=dict(size=10, color=GREY)))), "tb_roll")

    # ── Row 2: product flows | gap by coffee year ──
    l, r = st.columns([1.35, 1], gap="medium")
    with l, st.container(border=True):
        h, c = st.columns([1.2, 2], vertical_alignment="center")
        with h:
            card_head("Flows by product", "Imports up, exports down, net line · own tonnes (not GBE)")
        with c:
            prod = st.radio("Product", PRODUCTS, horizontal=True, key="tb_prod", label_visibility="collapsed")
        p = load_products()
        p = p[(p["product"] == prod) & (p["date"] <= last)].set_index("date").loc[since:]
        fig = go.Figure()
        fig.add_bar(x=p.index, y=p["imp_t"] * f, name="Imports", marker_color=TEAL, hovertemplate=f"Imports: %{{y:{fmt}}}<extra></extra>")
        fig.add_bar(x=p.index, y=-p["exp_t"] * f, name="Exports", marker_color=WINE, hovertemplate=f"Exports: %{{y:{fmt}}}<extra></extra>")
        net = (p["imp_t"] - p["exp_t"]) * f
        fig.add_scatter(x=p.index, y=net.rolling(12).mean(), name="Net, 12m avg", mode="lines", line=dict(color=NAVY, width=2),
                        hovertemplate=f"Net 12m avg: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, 380, barmode="relative", bargap=0.1, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "tb_prod_c")

    with r, st.container(border=True):
        cm_now = (last.month - 10) % 12 + 1
        cut = f"Oct–{MONTHS[cm_now - 1]}"
        card_head("Implied stock change by coffee year", f"Net imports − consumption, GBE · latest year = CYTD {cut}")
        y = m.copy()
        y["cy"] = [f"{(d.year - (d.month < 10)) % 100:02d}/{(d.year - (d.month < 10) + 1) % 100:02d}" for d in y.index]
        g = y.dropna(subset=["cons"]).groupby("cy")["gap"].sum() * f
        g = g.iloc[-14:]
        fig = go.Figure(go.Bar(x=g.index, y=g.values, marker_color=[TEAL if v >= 0 else RED for v in g.values],
                               text=[format(v, fmt) for v in g.values], textposition="outside", textfont=dict(size=9.5, color=AXIS),
                               cliponaxis=False, hovertemplate=f"%{{x}}: %{{y:{fmt}}} {suf}<extra></extra>"))
        show(base(fig, 380, legend=None, unified=False, bargap=0.35, yaxis=dict(tickformat=fmt)), "tb_gap_cy")

    # ── Row 3: re-export destinations | decaf hub ──
    l, r = st.columns(2, gap="medium")
    o = load_origins()
    o = o[o["date"] <= last]
    cur_cy = f"{(last.year - (last.month < 10)) % 100:02d}/{(last.year - (last.month < 10) + 1) % 100:02d}"
    prev_cy = f"{(last.year - (last.month < 10) - 1) % 100:02d}/{(last.year - (last.month < 10)) % 100:02d}"
    with l, st.container(border=True):
        card_head(f"Green coffee re-exports by destination, CYTD {cut}", f"{cur_cy} vs {prev_cy} · green incl. decaf")
        ex = o[o["cm"] <= cm_now].groupby(["cy", "country"])["exp_t"].sum()
        ec, ep = ex.get(cur_cy, pd.Series(dtype=float)), ex.get(prev_cy, pd.Series(dtype=float))
        top = ec.sort_values(ascending=False).index[:10][::-1]
        fig = go.Figure()
        fig.add_bar(y=top, x=ep.reindex(top).fillna(0) * f, name=prev_cy, orientation="h", marker_color=OTHER_C,
                    hovertemplate=f"%{{y}} {prev_cy}: %{{x:{fmt}}}<extra></extra>")
        fig.add_bar(y=top, x=ec.reindex(top) * f, name=cur_cy, orientation="h", marker_color=WINE,
                    hovertemplate=f"%{{y}} {cur_cy}: %{{x:{fmt}}}<extra></extra>")
        show(base(fig, 380, barmode="group", unified=False, bargap=0.25, xaxis=dict(tickformat=fmt, showgrid=True),
                  yaxis=dict(showgrid=False)), "tb_dest")

    with r, st.container(border=True):
        card_head("Decaf hub", "Green decaf imports vs roasted decaf exports (GBE), 12m rolling: Germany decaffeinates for Europe")
        dd = pd.DataFrame({"Green decaf imports": imp["Green decaf"], "Green decaf exports": exp["Green decaf"],
                           "Roasted decaf exports": exp["Roasted decaf"]}).rolling(12).sum().loc[since:] * f
        fig = go.Figure()
        for c, col, dash in [("Green decaf imports", TEAL, None), ("Green decaf exports", WINE, None), ("Roasted decaf exports", AMBER, "dot")]:
            fig.add_scatter(x=dd.index, y=dd[c], name=c, mode="lines", line=dict(color=col, width=2.2, dash=dash),
                            hovertemplate=f"{c}: %{{y:{fmt}}}<extra></extra>")
        show(base(fig, 380, xaxis=dict(tickformat="%Y"), yaxis=dict(tickformat=fmt)), "tb_decaf")

    # ── Table ──
    with st.container(border=True):
        card_head("Coffee-year balance, GBE", f"{unit} · imports and exports by product, net imports, tax consumption, implied stock change · latest = CYTD {cut}")
        y = m.join(imp.add_prefix("i_")).join(exp.add_prefix("e_"))
        y["cy"] = [f"{(d.year - (d.month < 10)) % 100:02d}/{(d.year - (d.month < 10) + 1) % 100:02d}" for d in y.index]
        t = y.groupby("cy").sum(min_count=1).iloc[-10:]
        cols = [("i_Green", "Green imp"), ("i_Roasted", "Roasted imp"), ("i_Soluble", "Soluble imp"), ("imp", "Total imp"),
                ("e_Green", "Green exp"), ("e_Roasted", "Roasted exp"), ("e_Soluble", "Soluble exp"), ("exp", "Total exp"),
                ("net", "Net imp"), ("cons", "Consumption"), ("gap", "Stock chg")]
        t["i_Green"] += t["i_Green decaf"]; t["i_Roasted"] += t["i_Roasted decaf"]
        t["e_Green"] += t["e_Green decaf"]; t["e_Roasted"] += t["e_Roasted decaf"]
        bold = {"imp", "exp", "net", "gap"}
        rows = []
        for cy, r_ in t.iloc[::-1].iterrows():
            rows.append([(cy + (" *" if cy == cur_cy else ""), "n")] +
                        [(format(r_[c] * f, fmt) if pd.notna(r_[c]) else "", "b" if c in bold else
                          ("up" if c == "gap" and r_[c] >= 0 else "")) for c, _ in cols])
        table(["Coffee year"] + [lbl for _, lbl in cols], rows)
        st.markdown(f"<div class='card-desc' style='margin-top:6px'>* CYTD {cut}. Green and roasted include decaf. "
                    "Consumption is the coffee-tax proxy (soluble is taxed at a higher rate, so it is an upper bound); "
                    "a persistent positive gap also absorbs conversion-factor and tax-timing error, not only real stock builds.</div>",
                    unsafe_allow_html=True)
